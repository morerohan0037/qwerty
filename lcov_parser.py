# lcov_to_mysql.py
import sys
from datetime import datetime
import mysql.connector

# ---------- MySQL connection config ----------
MYSQL_CONFIG = {
    'host': 'localhost',      # DevLake MySQL host
    'port': 3306,
    'user': 'merico',         # your MySQL user
    'password': 'merico',     # your MySQL password
    'database': 'lake'     # your DevLake DB
}

# optional: set repo and commit for this run
REPO_NAME = 'index-service'
COMMIT_SHA = 'abcdef1234'

# ---------- LCOV parsing ----------
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
                    current_file = line[3:]
                    total_lines = 0
                    covered_lines = 0
                    total_branches = 0
                    covered_branches = 0
                
                elif line.startswith('DA:'):
                    total_lines += 1
                    execution_count = int(line.split(',')[1])
                    if execution_count > 0:
                        covered_lines += 1
                
                elif line.startswith('BRDA:'):
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

# ---------- Insert coverage data into MySQL ----------
def push_to_mysql(coverage_data):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        run_timestamp = datetime.utcnow()

        # Before inserting
        cursor.execute(
            "DELETE FROM code_coverage WHERE repo=%s AND commit_sha=%s",
            (REPO_NAME, COMMIT_SHA)
        )
        conn.commit()

        
        insert_query = """
        INSERT INTO code_coverage (
            repo, commit_sha, run_timestamp, file_path,
            total_lines, covered_lines, uncovered_lines, coverage_percent,
            total_branches, covered_branches, uncovered_branches, branch_coverage_percent
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        
        for row in coverage_data:
            cursor.execute(insert_query, (
                REPO_NAME,
                COMMIT_SHA,
                run_timestamp,
                row['filepath'],
                row['total_lines'],
                row['covered_lines'],
                row['uncovered_lines'],
                row['coverage_percent'],
                row['total_branches'],
                row['covered_branches'],
                row['uncovered_branches'],
                row['branch_coverage_percent']
            ))
        
        conn.commit()
        print(f"✅ Inserted {len(coverage_data)} rows into code_coverage")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error inserting into MySQL: {e}")

# ---------- Main ----------
# ---------- Main ----------
def main():
    if len(sys.argv) < 3:
        print("Usage: python lcov_to_mysql.py <path_to_lcov_file> <repo_name> [commit_sha]")
        return
    
    lcov_file = sys.argv[1]
    repo_name = sys.argv[2]
    commit_sha = sys.argv[3] if len(sys.argv) > 3 else 'default-sha'

    global REPO_NAME, COMMIT_SHA
    REPO_NAME = repo_name
    COMMIT_SHA = commit_sha

    coverage_data = parse_lcov_file(lcov_file)
    if coverage_data:
        push_to_mysql(coverage_data)
    else:
        print("No coverage data to insert.")


if __name__ == "__main__":
    main()
