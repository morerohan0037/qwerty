# d:\GrIntern\program\lcov_parser.py
import sys
import csv
from datetime import datetime

def parse_lcov_file(lcov_file_path):
    results = []
    current_file = None
    total_lines = 0
    covered_lines = 0
    total_branches = 0
    covered_branches = 0
    
    try:
        with open(lcov_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                
                if line.startswith('SF:'):
                    # New file entry
                    if current_file:
                        coverage_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0
                        branch_percent = (covered_branches / total_branches * 100) if total_branches > 0 else 0
                        results.append({
                            'filepath': current_file,
                            'total_lines': total_lines,
                            'covered_lines': covered_lines,
                            'uncovered_lines': total_lines - covered_lines,
                            'coverage_percent': round(coverage_percent, 2),
                            'total_branches': total_branches,
                            'covered_branches': covered_branches,
                            'uncovered_branches': total_branches - covered_branches,
                            'branch_coverage_percent': round(branch_percent, 2)
                        })
                    
                    current_file = line[3:]  # Remove 'SF:' prefix
                    total_lines = 0
                    covered_lines = 0
                    total_branches = 0
                    covered_branches = 0
                
                elif line.startswith('DA:'):
                    total_lines += 1
                    # DA:line_number,execution_count
                    execution_count = int(line.split(',')[1])
                    if execution_count > 0:
                        covered_lines += 1
                
                elif line.startswith('BRDA:'):
                    # BRDA:line_number,block_number,branch_number,taken
                    total_branches += 1
                    parts = line.split(',')
                    if parts[3] != '-' and int(parts[3]) > 0:
                        covered_branches += 1
        
        # Add the last file
        if current_file:
            coverage_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            branch_percent = (covered_branches / total_branches * 100) if total_branches > 0 else 0
            results.append({
                'filepath': current_file,
                'total_lines': total_lines,
                'covered_lines': covered_lines,
                'uncovered_lines': total_lines - covered_lines,
                'coverage_percent': round(coverage_percent, 2),
                'total_branches': total_branches,
                'covered_branches': covered_branches,
                'uncovered_branches': total_branches - covered_branches,
                'branch_coverage_percent': round(branch_percent, 2)
            })
                    
        return results
    
    except Exception as e:
        print(f"Error processing LCOV file: {str(e)}")
        return []

def write_to_csv(coverage_data, output_file=None):
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'coverage_report_{timestamp}.csv'
    
    fieldnames = [
        'filepath', 'total_lines', 'covered_lines', 'uncovered_lines', 
        'coverage_percent', 'total_branches', 'covered_branches', 
        'uncovered_branches', 'branch_coverage_percent'
    ]
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(coverage_data)
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python lcov_parser.py <path_to_lcov_file> [output_csv_file]")
        return
    
    lcov_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    coverage_data = parse_lcov_file(lcov_file)
    if coverage_data:
        output_path = write_to_csv(coverage_data, output_file)
        print(f"\nCoverage data has been written to: {output_path}")
    else:
        print("No coverage data was generated.")

if __name__ == "__main__":
    main()