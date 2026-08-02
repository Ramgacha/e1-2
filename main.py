import json
import os
import sys

class Quiz:
    """개별 퀴즈 1개를 표현하는 클래스"""
    
    def __init__(self, question: str, choices: list, answer: int):
        self.question = question  # str(문자열): 문제 내용
        self.choices = choices    # list(리스트): 1~4번 선택지 목록
        self.answer = answer      # int(정수): 정답 번호(1~4)

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"]
        )

    def print_quiz(self, index: int):
        print(f"\n[{index}] {self.question}")
        for i, choice in enumerate(self.choices, 1):
            print(f"   {i}. {choice}")

    def check_answer(self, user_answer: int) -> bool:
        return self.answer == user_answer


class QuizGame:
    """게임 전체를 관리하는 클래스"""
    def __init__(self, state_file="state.json"):
        self.state_file = state_file  # 데이터 저장할 파일 이름
        self.quizzes = []             # 퀴즈 목록 (Quiz 객체들이 들어가는 리스트)
        self.best_score = 0           # 최고 점수 (int)
        self.load_data()              # 게임이 시작되자마자 저장된 데이터 로드!

    def get_default_quizzes(self) -> list:
        """처음 시작할 때 기본으로 넣어줄 5개 퀴즈 (주제: 파이썬/Git)"""
        return [
            Quiz("Python을 개발한 창시자의 이름은?", ["구이도 반 로섬", "제임스 고슬링", "리너스 토발즈", "데니스 리치"], 1),
            Quiz("파이썬에서 리스트를 정렬할 때 사용하는 내장 메서드는?", ["order()", "align()", "sort()", "arrange()"], 3),
            Quiz("JSON 형식에서 문자열을 감싸는 기호는?", ["작은따옴표('')", "큰따옴표(\"\")", "백틱(``)", "괄호(())"], 2),
            Quiz("Git에서 원격 저장소의 변경사항을 로컬로 가져와 병합하는 명령어는?", ["git fetch", "git push", "git clone", "git pull"], 4),
            Quiz("다음 중 파이썬의 불변(Immutable) 데이터 타입은?", ["List", "Dictionary", "Set", "Tuple"], 4)
        ]

    def load_data(self):
        """state.json 파일에서 데이터를 읽어오는 기능"""
        if not os.path.exists(self.state_file):
            print("📂 저장된 데이터가 없어 기본 퀴즈 데이터를 로드합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.quizzes = [Quiz.from_dict(q) for q in data.get("quizzes", [])]
                self.best_score = data.get("best_score", 0)
                if not self.quizzes:
                    self.quizzes = self.get_default_quizzes()
                print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")
        except (json.JSONDecodeError, KeyError, Exception):
            print("⚠️ 데이터 파일이 손상되었습니다. 기본 퀴즈 데이터로 초기화합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0

    def save_data(self):
        """state.json 파일에 현재 상태를 저장하는 기능"""
        try:
            data = {
                "quizzes": [q.to_dict() for q in self.quizzes],
                "best_score": self.best_score
            }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ 데이터 저장 중 오류 발생: {e}")

    def safe_input(self, prompt: str, min_val: int = None, max_val: int = None) -> int:
        """예외 처리가 완벽히 적용된 숫자 입력 전용 메서드"""
        while True:
            try:
                user_str = input(prompt).strip()
                if not user_str:
                    print("⚠️ 빈 입력입니다. 숫자를 입력해주세요.")
                    continue
                
                val = int(user_str)
                if min_val is not None and max_val is not None:
                    if val < min_val or val > max_val:
                        print(f"⚠️ 잘못된 입력입니다. {min_val}-{max_val} 사이의 숫자를 입력하세요.")
                        continue
                        
                return val
                
            except ValueError:
                if min_val is not None and max_val is not None:
                    print(f"⚠️ 잘못된 입력입니다. {min_val}-{max_val} 사이의 숫자를 입력하세요.")
                else:
                    print("⚠️ 숫자를 입력해주세요.")

    def play_quiz(self):
        """1. 퀴즈 풀기"""
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다! 퀴즈를 먼저 추가해주세요.")
            return

        print(f"\n📝 퀴즈를 시작합니다! (총 {len(self.quizzes)}문제)")
        print("-" * 40)
        correct_count = 0

        for idx, quiz in enumerate(self.quizzes, 1):
            quiz.print_quiz(f"문제 {idx}")
            answer = self.safe_input("\n정답 입력 (1-4): ", 1, 4)
            
            if quiz.check_answer(answer):
                print("✅ 정답입니다!")
                correct_count += 1
            else:
                print(f"❌ 오답입니다. (정답: {quiz.answer}번)")
            print("-" * 40)

        total_questions = len(self.quizzes)
        score = int((correct_count / total_questions) * 100)
        print(f"\n========================================")
        print(f"🏆 결과: {total_questions}문제 중 {correct_count}문제 정답! ({score}점)")
        
        if score > self.best_score:
            self.best_score = score
            print("🎉 새로운 최고 점수입니다!")
            self.save_data()
        print(f"========================================")

    def add_quiz(self):
        """2. 퀴즈 추가"""
        print("\n📌 새로운 퀴즈를 추가합니다.")
        question = input("문제를 입력하세요: ").strip()
        while not question:
            print("⚠️ 문제는 빈칸일 수 없습니다.")
            question = input("문제를 입력하세요: ").strip()

        choices = []
        for i in range(1, 5):
            choice = input(f"선택지 {i}: ").strip()
            while not choice:
                print("⚠️ 선택지는 빈칸일 수 없습니다.")
                choice = input(f"선택지 {i}: ").strip()
            choices.append(choice)

        answer = self.safe_input("정답 번호 (1-4): ", 1, 4)

        new_quiz = Quiz(question, choices, answer)
        self.quizzes.append(new_quiz)
        self.save_data()
        print("\n✅ 퀴즈가 성공적으로 추가되었습니다!")

    def show_list(self):
        """3. 퀴즈 목록 보기"""
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다!")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for idx, quiz in enumerate(self.quizzes, 1):
            print(f"[{idx}] {quiz.question}")
        print("-" * 40)

    def show_best_score(self):
        """4. 최고 점수 확인"""
        print(f"\n🏆 역대 최고 점수: {self.best_score}점")

    def run(self):
        """게임의 주 메뉴를 계속 띄워주는 메인 루프 (while True)"""
        while True:
            print("\n========================================")
            print("        🎯 나만의 퀴즈 게임 🎯        ")
            print("========================================")
            print("1. 퀴즈 풀기")
            print("2. 퀴즈 추가")
            print("3. 퀴즈 목록")
            print("4. 점수 확인")
            print("5. 종료")
            print("========================================")

            choice = self.safe_input("선택: ", 1, 5)

            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_list()
            elif choice == 4:
                self.show_best_score()
            elif choice == 5:
                self.save_data()
                print("프로그램을 종료합니다. 감사합니다! 🚀")
                break


if __name__ == "__main__":
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\n⚠️ 비정상 입력이 감지되어 프로그램을 안전하게 종료합니다.")
        game.save_data()
        sys.exit(0)