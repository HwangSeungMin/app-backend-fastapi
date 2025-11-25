"""
원본 RAG와 통합된 버전 비교
"""
import os
import hashlib
from pathlib import Path

def get_file_hash(filepath):
    """파일의 MD5 해시 계산"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def compare_directories():
    """디렉토리 비교"""
    base_original = Path("d:/yakkobak_be/temp_compare")
    base_integrated = Path("d:/yakkobak_be")
    
    # 매핑: 원본 경로 -> 통합 경로
    path_mapping = {
        "api": "app/api/v1/endpoints/rag",
        "config": "app/core",
        "search": "app/search",
        "services": "app/services/rag",
        "utils": "app/utils",
        "data": "data",
        "scripts": "scripts",
        "docs": "docs",
    }
    
    print("=" * 80)
    print("파일 비교 분석")
    print("=" * 80)
    
    missing_files = []
    different_files = []
    
    for orig_dir, integ_dir in path_mapping.items():
        orig_path = base_original / orig_dir
        integ_path = base_integrated / integ_dir
        
        if not orig_path.exists():
            continue
            
        print(f"\n[{orig_dir}/ -> {integ_dir}/]")
        
        for root, dirs, files in os.walk(orig_path):
            # __pycache__ 제외
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith('.pyc') or file == '__pycache__':
                    continue
                    
                orig_file = Path(root) / file
                rel_path = orig_file.relative_to(orig_path)
                
                # 통합 버전에서 대응되는 파일 경로
                integ_file = integ_path / rel_path
                
                if not integ_file.exists():
                    missing_files.append({
                        'original': str(orig_file),
                        'expected': str(integ_file),
                        'rel_path': str(rel_path)
                    })
                    print(f"  ✗ 누락: {rel_path}")
                else:
                    # 파일 해시 비교
                    orig_hash = get_file_hash(orig_file)
                    integ_hash = get_file_hash(integ_file)
                    
                    if orig_hash != integ_hash:
                        different_files.append({
                            'original': str(orig_file),
                            'integrated': str(integ_file),
                            'rel_path': str(rel_path)
                        })
                        print(f"  ⚠ 차이: {rel_path}")
    
    print("\n" + "=" * 80)
    print(f"요약: 누락 {len(missing_files)}개, 차이 {len(different_files)}개")
    print("=" * 80)
    
    # 결과 저장
    with open("comparison_report.txt", "w", encoding="utf-8") as f:
        f.write("=== 누락된 파일 ===\n\n")
        for item in missing_files:
            f.write(f"{item['rel_path']}\n")
            f.write(f"  원본: {item['original']}\n")
            f.write(f"  위치: {item['expected']}\n\n")
        
        f.write("\n=== 내용이 다른 파일 ===\n\n")
        for item in different_files:
            f.write(f"{item['rel_path']}\n")
            f.write(f"  원본: {item['original']}\n")
            f.write(f"  통합: {item['integrated']}\n\n")
    
    print("\n상세 보고서: comparison_report.txt")
    
    return missing_files, different_files

if __name__ == "__main__":
    compare_directories()
