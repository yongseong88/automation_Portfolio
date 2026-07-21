import filecmp
import json
import os
import pathlib
from configparser import ConfigParser

class Filereadutil():

    def readConfig(self, section, key):
        env_key = f"{section.upper()}_{key.upper()}"

        if env_key in os.environ:  # CI: 환경변수 있으면 그걸 씀
            return os.environ[env_key]

        # 로컬: 환경변수 없으면 config.ini 읽음
        config = ConfigParser()
        config.read(self.read_filepath("Config", "config.ini"))
        return config.get(section, key)

    def write_file(self, input_file_path, file_data):

        try:
            # file_data = self.read_file(input_file_path)

            if file_data is None:
                print("file_data가 없어요")
                return  # 읽기 실패 시 종료

            source_folder_path = os.path.dirname(input_file_path)  # '/Users/data' 폴더 경로
            file_name_with_ext = os.path.basename(input_file_path)  # 'doc.json' 파일 경로
            file_extension = os.path.splitext(file_name_with_ext)[1].lower() # 확장자 구분

            # 3. 임시 저장 경로 설정
            # 비교를 위해 원본 파일과 동일한 내용의 임시 파일을 생성할 경로
            # temp_file_path = os.path.join(source_folder_path, f".temp_{file_name_with_ext}")

            if file_extension == '.json':

                # 4. 임시 파일에 새 내용을 저장
                os.makedirs(source_folder_path, exist_ok=True)

                with open(input_file_path, 'w', encoding="utf-8") as file:
                    # 새로운 내용을 임시 파일에 JSON 형식으로 저장
                    json.dump(file_data, file, indent=4, ensure_ascii=False)

            else:
                print(f"⚠️ 쓰기 작업을 지원하지 않는 파일 형식입니다: {file_extension}")

        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {input_file_path}")

        except Exception as e:
            print(f"❌ 파일 쓰기 중 오류 발생: {e}")


    def read_file(self, file_path):
        # 파일 경로에서 확장자 추출 (예: "data.json" -> ".json")
        file_extension = os.path.splitext(file_path)[1].lower()

        try:

            if not os.path.exists(file_path):
                print(f"파일을 찾을 수 없습니다: {file_path}")
                return None

            if os.path.getsize(file_path) == 0:
                print(f"⚠️ 파일이 비어 있습니다: {file_path}")
                return [] if file_extension == '.json' else None  # JSON이면 빈 리스트 반환 등 대응

            with open(file_path, 'r', encoding="utf-8") as file:

                if file_extension == '.json':
                    # JSON 파일인 경우: json.load()를 사용하여 데이터 구조를 로드
                    data = json.load(file)
                    return data

                elif file_extension == '.txt':
                    multiline_list = []

                    # TXT 파일인 경우: 파일의 내용을 문자열로 읽어옴
                    lines = file.readlines()
                    print(f"✅ 텍스트 파일 내용 로드 완료: {file_path}")

                    for line in lines:
                        multiline_list.append(line.strip())

                    return multiline_list

                else:
                    print(f"⚠️ 지원하지 않는 파일 형식입니다: {file_extension}")
                    return None

        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {file_path}")
            return None

        except json.JSONDecodeError:
            print(f"JSON 디코딩 오류가 발생했습니다: {file_path}")
            return None

    def read_filepath(self, root_dir, file_name):

        """

            현재 스크립트의 위치를 기준으로 절대 경로를 계산하여 반환합니다.

            (root_dir="Config", file_name="upload_file.json")

        """

        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = str(pathlib.Path(current_script_dir).parent)

        full_file_path = os.path.join(base_dir, root_dir, file_name)

        return full_file_path

