import os
import sys
import csv
import gzip
import shutil
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt

ALGORITHMS = ['rle', 'hce', 'lz77', 'defl']
TEST_DIR = 'canterbury-corpus-master'
OUTPUT_DIR = 'benchmark_output'
CSV_FILE = 'benchmark_results.csv'
CHARTS_DIR = 'benchmark_charts'

# create necessary directories
def make_dirs():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(CHARTS_DIR).mkdir(exist_ok=True)

# get list of test files
def get_test_files():
    test_path = Path(TEST_DIR)
    if not test_path.exists():
        print(f"Error: {TEST_DIR} not found!")
        sys.exit(1)
    
    files = []
    for root, _, filenames in os.walk(test_path):
        for filename in filenames:
            filepath = Path(root) / filename
            if not filename.startswith('.') and filepath.is_file():
                files.append(filepath)
    
    return sorted(files)

# get file size
def get_size(filepath):
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0

# compress using CLI
def compress_cli(input_file, algo, output_dir):
    try:
        out_path = Path(output_dir)
        before = set()
        if out_path.exists():
            for root, dirs, files in os.walk(out_path):
                for f in files:
                    before.add(Path(root) / f)
        
        cmd = [
            'python3',
            'compressor_tool/cli.py',
            algo,
            str(input_file),
            output_dir
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"  {algo.upper()}: FAILED")
            if result.stderr:
                print(f"    Error: {result.stderr.strip()[:100]}")
            return None, False
        
        after = set()
        if out_path.exists():
            for root, dirs, files in os.walk(out_path):
                for f in files:
                    after.add(Path(root) / f)
        
        new = after - before
        
        if new:
            out_file = list(new)[0]
            return out_file, True
        
        print(f"  {algo.upper()}: FAILED (no output file)")
        return None, False

    # handle timeouts and exceptions    
    except subprocess.TimeoutExpired:
        print(f"  {algo.upper()}: TIMEOUT")
        return None, False
    except Exception as e:
        print(f"  {algo.upper()}: ERROR - {str(e)[:50]}")
        return None, False

# compress using gzip
def compress_gzip(input_file, output_dir):
    try:
        out_file = Path(output_dir) / f"{input_file.name}.gz"
        
        with open(input_file, 'rb') as f_in:
            with gzip.open(out_file, 'wb', compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return out_file, True
        
    except Exception as e:
        print(f"  GZIP: ERROR - {str(e)[:50]}")
        return None, False

# run benchmark tests
def run_tests():
    print("=" * 70)
    print("File Compression Benchmark - Canterbury Corpus")
    print("=" * 70)
    print()
    
    # create necessary directories
    make_dirs()
    test_files = get_test_files()
    
    print(f"Found {len(test_files)} files to test")
    print()
    
    # open CSV file for writing results
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fields = [
            'file_name',
            'original_size',
            'algorithm',
            'compressed_size',
            'compression_ratio',
            'space_savings_pct',
            'success'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        
        for idx, file in enumerate(test_files, 1):
            print(f"[{idx}/{len(test_files)}] {file.name} ({file.parent.name}/)")
            
            orig_size = get_size(file)
            if orig_size == 0:
                print(f"  Skipping empty file")
                continue
            
            print(f"  Original: {orig_size:,} bytes")
            
            results = []
            
            for algo in ALGORITHMS + ['gzip']:
                if algo == 'gzip':
                    out_file, ok = compress_gzip(file, OUTPUT_DIR)
                else:
                    out_file, ok = compress_cli(file, algo, OUTPUT_DIR)
                
                if ok and out_file and out_file.exists():
                    comp_size = get_size(out_file)
                    ratio = orig_size / comp_size if comp_size > 0 else 0
                    saved = ((orig_size - comp_size) / orig_size * 100) if orig_size > 0 else 0
                    
                    results.append(f"{algo.upper()}: {comp_size:,} bytes ({ratio:.2f}x)")
                    
                    try:
                        out_file.unlink()
                    except:
                        pass
                else:
                    comp_size = 0
                    ratio = 0
                    saved = 0
                    results.append(f"{algo.upper()}: FAILED")
                
                writer.writerow({
                    'file_name': file.name,
                    'original_size': orig_size,
                    'algorithm': algo,
                    'compressed_size': comp_size,
                    'compression_ratio': f"{ratio:.4f}",
                    'space_savings_pct': f"{saved:.2f}",
                    'success': ok
                })
            
            for result in results:
                print(f"  {result}")
            print()
    
    print("=" * 70)
    print(f"Results saved to: {CSV_FILE}")
    print()

# generate charts from results
def make_charts():
    print("Making charts...")
    
    data = {algo: {'ratios': [], 'orig': [], 'comp': [], 'files': []} 
            for algo in ALGORITHMS + ['gzip']}
    
    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['success'] == 'True' and float(row['compression_ratio']) > 0:
                algo = row['algorithm']
                data[algo]['ratios'].append(float(row['compression_ratio']))
                data[algo]['orig'].append(int(row['original_size']))
                data[algo]['comp'].append(int(row['compressed_size']))
                data[algo]['files'].append(row['file_name'])
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    names = []
    avg_ratios = []
    
    for algo in ALGORITHMS + ['gzip']:
        if data[algo]['ratios']:
            names.append(algo.upper())
            avg_ratios.append(sum(data[algo]['ratios']) / len(data[algo]['ratios']))
    
    # create bar chart for average compression ratios
    bars = ax.bar(names, avg_ratios, color=colors[:len(names)], 
                   edgecolor='black', linewidth=1.5, alpha=0.8)
    ax.set_ylabel('Average Compression Ratio', fontsize=13, fontweight='bold')
    ax.set_xlabel('Algorithm', fontsize=13, fontweight='bold')
    ax.set_title('Average Compression Ratio by Algorithm\n(Higher is Better)', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, 
               label='No Compression (1.0x)', alpha=0.7)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}x',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/compression_ratio.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    names = []
    saved_mb = []
    
    # create bar chart for total space saved
    for algo in ALGORITHMS + ['gzip']:
        if data[algo]['orig']:
            names.append(algo.upper())
            orig_total = sum(data[algo]['orig'])
            comp_total = sum(data[algo]['comp'])
            mb = (orig_total - comp_total) / (1024 * 1024)
            saved_mb.append(mb)
    
    bars = ax.bar(names, saved_mb, color=colors[:len(names)], 
                   edgecolor='black', linewidth=1.5, alpha=0.8)
    ax.set_ylabel('Total Space Saved (MB)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Algorithm', fontsize=13, fontweight='bold')
    ax.set_title('Total Space Saved Across All Files\n(Higher is Better)', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f} MB',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/space_saved.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    names = []
    success_pct = []
    
    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        stats = {algo: {'ok': 0, 'total': 0} for algo in ALGORITHMS + ['gzip']}
        
        for row in reader:
            algo = row['algorithm']
            stats[algo]['total'] += 1
            if row['success'] == 'True':
                stats[algo]['ok'] += 1
        
        for algo in ALGORITHMS + ['gzip']:
            if stats[algo]['total'] > 0:
                names.append(algo.upper())
                pct = (stats[algo]['ok'] / stats[algo]['total']) * 100
                success_pct.append(pct)
    
    bars = ax.bar(names, success_pct, color=colors[:len(names)], 
                   edgecolor='black', linewidth=1.5, alpha=0.8)
    ax.set_ylabel('Success Rate (%)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Algorithm', fontsize=13, fontweight='bold')
    ax.set_title('Compression Success Rate by Algorithm', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/success_rate.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Charts saved to: {CHARTS_DIR}/")
    print("  - compression_ratio.png")
    print("  - space_saved.png")
    print("  - success_rate.png")

# print benchmark summary
def print_summary():
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    
    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        stats = {algo: {
            'count': 0,
            'ok': 0,
            'total_ratio': 0,
            'total_saved': 0,
            'orig_bytes': 0,
            'comp_bytes': 0
        } for algo in ALGORITHMS + ['gzip']}
        
        for row in reader:
            algo = row['algorithm']
            stats[algo]['count'] += 1
            
            if row['success'] == 'True':
                stats[algo]['ok'] += 1
                stats[algo]['total_ratio'] += float(row['compression_ratio'])
                stats[algo]['total_saved'] += float(row['space_savings_pct'])
                stats[algo]['orig_bytes'] += int(row['original_size'])
                stats[algo]['comp_bytes'] += int(row['compressed_size'])
    
    for algo in ALGORITHMS + ['gzip']:
        s = stats[algo]
        if s['count'] > 0:
            ok_pct = (s['ok'] / s['count']) * 100
            avg_ratio = s['total_ratio'] / s['ok'] if s['ok'] > 0 else 0
            avg_saved = s['total_saved'] / s['ok'] if s['ok'] > 0 else 0
            mb_saved = (s['orig_bytes'] - s['comp_bytes']) / (1024 * 1024)
            
            print(f"\n{algo.upper()}:")
            print(f"  Files Processed: {s['count']} ({s['ok']} successful)")
            print(f"  Success Rate: {ok_pct:.1f}%")
            print(f"  Avg Compression Ratio: {avg_ratio:.2f}x")
            print(f"  Avg Space Savings: {avg_saved:.2f}%")
            print(f"  Total Space Saved: {mb_saved:.2f} MB")
    
    print("\n" + "=" * 70)

# main execution
if __name__ == '__main__':
    try:
        run_tests()
        make_charts()
        print_summary()
        print("\nBenchmark complete! Check the output files for detailed results.")
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)