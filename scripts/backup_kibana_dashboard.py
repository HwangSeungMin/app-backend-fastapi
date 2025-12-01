"""
Kibana 대시보드 백업 스크립트
현재 구성된 대시보드를 NDJSON 파일로 내보내기
"""
import requests
import json
from datetime import datetime
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)

KIBANA_URL = "http://localhost:5601"
BACKUP_DIR = Path("backups/kibana")

def ensure_backup_dir():
    """백업 디렉토리 생성"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"백업 디렉토리: {BACKUP_DIR.absolute()}")

def export_dashboard():
    """대시보드 및 관련 객체 내보내기"""
    logger.info("Kibana 대시보드 내보내기 시작...")

    url = f"{KIBANA_URL}/api/saved_objects/_export"
    
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }

    # 내보낼 객체 타입
    data = {
        "type": [
            "dashboard",
            "visualization",
            "index-pattern",
            "search"
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # 타임스탬프를 포함한 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = BACKUP_DIR / f"kibana_dashboard_{timestamp}.ndjson"
            
            # NDJSON 파일로 저장
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✓ 대시보드 백업 완료: {filename}")
            
            # 백업 내용 분석
            analyze_backup(filename)
            
            return True
        else:
            logger.error(f"대시보드 내보내기 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"대시보드 내보내기 오류: {e}")
        return False

def analyze_backup(filename):
    """백업 파일 내용 분석"""
    logger.info("\n📊 백업 내용 분석:")
    
    counts = {
        "index-pattern": 0,
        "visualization": 0,
        "dashboard": 0,
        "search": 0
    }
    
    visualizations = []
    dashboards = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line)
                    obj_type = obj.get("type")
                    
                    if obj_type in counts:
                        counts[obj_type] += 1
                    
                    if obj_type == "visualization":
                        title = obj.get("attributes", {}).get("title", "Unknown")
                        visualizations.append(title)
                    elif obj_type == "dashboard":
                        title = obj.get("attributes", {}).get("title", "Unknown")
                        dashboards.append(title)
        
        # 결과 출력
        logger.info(f"  - 인덱스 패턴: {counts['index-pattern']}개")
        logger.info(f"  - 시각화: {counts['visualization']}개")
        logger.info(f"  - 대시보드: {counts['dashboard']}개")
        logger.info(f"  - 저장된 검색: {counts['search']}개")
        
        if visualizations:
            logger.info("\n📈 시각화 목록:")
            for viz in visualizations:
                logger.info(f"  - {viz}")
        
        if dashboards:
            logger.info("\n📋 대시보드 목록:")
            for dash in dashboards:
                logger.info(f"  - {dash}")
                
    except Exception as e:
        logger.error(f"백업 분석 오류: {e}")

def import_dashboard(filename):
    """백업 파일에서 대시보드 복원"""
    logger.info(f"대시보드 복원 시작: {filename}")

    url = f"{KIBANA_URL}/api/saved_objects/_import"
    
    headers = {
        "kbn-xsrf": "true"
    }

    try:
        with open(filename, 'rb') as f:
            files = {'file': (filename.name, f, 'application/ndjson')}
            response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ 대시보드 복원 완료")
            logger.info(f"  - 성공: {result.get('successCount', 0)}개")
            
            if result.get('errors'):
                logger.warning(f"  - 오류: {len(result['errors'])}개")
                for error in result['errors'][:5]:  # 처음 5개만 표시
                    logger.warning(f"    • {error.get('error', {}).get('message', 'Unknown error')}")
            
            return True
        else:
            logger.error(f"대시보드 복원 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"대시보드 복원 오류: {e}")
        return False

def list_backups():
    """백업 파일 목록 조회"""
    logger.info("백업 파일 목록:")
    
    if not BACKUP_DIR.exists():
        logger.warning("백업 디렉토리가 없습니다.")
        return []
    
    backups = sorted(BACKUP_DIR.glob("kibana_dashboard_*.ndjson"), reverse=True)
    
    if not backups:
        logger.info("  백업 파일이 없습니다.")
        return []
    
    for i, backup in enumerate(backups, 1):
        size = backup.stat().st_size / 1024  # KB
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        logger.info(f"  {i}. {backup.name} ({size:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    return backups

def main():
    """메인 함수"""
    import sys
    
    logger.info("=" * 80)
    logger.info("Kibana 대시보드 백업/복원 도구")
    logger.info("=" * 80)
    
    ensure_backup_dir()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "export":
            export_dashboard()
        elif command == "import":
            if len(sys.argv) > 2:
                filename = Path(sys.argv[2])
                if filename.exists():
                    import_dashboard(filename)
                else:
                    logger.error(f"파일을 찾을 수 없습니다: {filename}")
            else:
                logger.error("사용법: python backup_kibana_dashboard.py import <파일경로>")
        elif command == "list":
            list_backups()
        else:
            logger.error(f"알 수 없는 명령: {command}")
            print_usage()
    else:
        # 기본 동작: 백업 생성
        export_dashboard()
        logger.info("\n" + "=" * 80)
        list_backups()

def print_usage():
    """사용법 출력"""
    logger.info("\n사용법:")
    logger.info("  python backup_kibana_dashboard.py              # 백업 생성")
    logger.info("  python backup_kibana_dashboard.py export       # 백업 생성")
    logger.info("  python backup_kibana_dashboard.py import <파일> # 백업 복원")
    logger.info("  python backup_kibana_dashboard.py list         # 백업 목록")

if __name__ == "__main__":
    main()
