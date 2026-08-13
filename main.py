import json
import os
import sys
import random
from datetime import datetime

class Quiz:
    """개별 퀴즈 1개를 표현하는 클래스"""
    #  [힌트 추가 1] 기본 매개변수로 hint 추가 (기존 코드와 호환 유지)
    def __init__(self, question: str, choices: list, answer: int, hint: str = "힌트가 없습니다."):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint #  [힌트 추가 2] 저장할 데이터에 포함
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
            #  기존 state.json 파일에 hint가 없어도 에러가 나지 않도록 get() 사용
            hint=data.get("hint", "힌트가 없습니다.")
        )

    def print_quiz(self, index: str):
        print(f"\n[{index}] {self.question}")
        for i, choice in enumerate(self.choices, 1):
            print(f"   {i}. {choice}")

    def check_answer(self, user_answer: int) -> bool:
        return self.answer == user_answer


class QuizGame:
    """게임 전체를 관리하는 클래스"""
    def __init__(self, state_file="state.json"):
        self.state_file = state_file
        self.quizzes = []
        self.best_score = 0
        self.load_data()

    def get_default_quizzes(self) -> list:
        #  [힌트 데이터 추가] 기본 퀴즈 5개에 힌트 부여
        return [
            Quiz("나의 이름은?", ["차우람", "차세람", "차가람", "람가차"], 3, "이름에 '가'가 들어갑니다."),
            Quiz("나의 롤 최고 티어는?", ["다이아몬드", "마스터", "그랜드마스터", "챌린저"], 4, "가장 높은 티어입니다."),
            Quiz("내가 밴드부 정기공연에서 맡은 적이 없는 세션은?", ["기타", "베이스", "드럼", "건반"], 3, "비트를 담당하는 타악기입니다."),
            Quiz("내가 좋아하는 아티스트는?", ["한로로", "유다빈밴드", "케로로밴드", "The Weeknd"], 4, "Blinding Lights!"),
            Quiz("2-handled torus의 second homology group은?", ["\033[1mZ\033[0m", "\033[1mZ\033[0m²", "\033[1mZ\033[0m³", "\033[1mZ\033[0m⁴"], 1, "정수군 1개로 표현됩니다.")
         ]

    def load_data(self):
        if not os.path.exists(self.state_file):
            print(" 저장된 데이터가 없어 기본 퀴즈 데이터를 로드합니다.")
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
                print(f" 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")
        except (json.JSONDecodeError, KeyError, Exception):
            print(" 데이터 파일이 손상되었습니다. 기본 퀴즈 데이터로 초기화합니다.")
            self.quizzes = self.get_default_quizzes()
            self.best_score = 0

    def save_data(self):
        try:
            data = {
                "quizzes": [q.to_dict() for q in self.quizzes],
                "best_score": self.best_score
            }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f" 데이터 저장 중 오류 발생: {e}")

    
    def safe_input(self, prompt: str, min_val: int = None, max_val: int = None) -> int:
        while True:
            try:
                user_str = input(prompt).strip()
                if not user_str:
                    print(" 빈 입력입니다. 숫자를 입력해주세요.")
                    continue
                
                val = int(user_str)
                if min_val is not None and max_val is not None:
                    if val < min_val or val > max_val:
                        print(f" 잘못된 입력입니다. {min_val}-{max_val} 사이의 숫자를 입력하세요.")
                        continue
                        
                return val
                
            except ValueError:
                if min_val is not None and max_val is not None:
                    print(f" 잘못된 입력입니다. {min_val}-{max_val} 사이의 숫자를 입력하세요.")
                else:
                    print(" 숫자를 입력해주세요.")

    #  [점수 기록 기능 추가 1]
    def save_history(self, count: int, score: int):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("history.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] 푼 문제 수: {count}개, 획득 점수: {score}점\n")

    def play_quiz(self):
        if not self.quizzes:
            print(" 등록된 퀴즈가 없습니다! 퀴즈를 먼저 추가해주세요.")
            return

        # 💡 [랜덤 출제 & 문제 수 선택 기능]
        print(f"\n 총 {len(self.quizzes)}문제가 있습니다.")
        count = self.safe_input(" 몇 문제를 푸시겠습니까?: ", 1, len(self.quizzes))
        
        # 원본을 망가뜨리지 않고 무작위로 count개 만큼 뽑아옵니다.
        play_list = random.sample(self.quizzes, count)

        print(f"\n 퀴즈를 시작합니다! (총 {count}문제)")
        print("-" * 40)
        
        score = 0

        for idx, quiz in enumerate(play_list, 1):
            quiz.print_quiz(f"문제 {idx}")
            
            point = 10 #  기본 점수 10점

            #  [힌트 차감 로직] 기존 safe_input 대신 'h'를 받아야 하므로 별도 처리
            while True:
                user_str = input("\n정답 입력 (1-4, 힌트 보기 'h'): ").strip().lower()
                
                if user_str == 'h':
                    if point == 10:
                        print(f"  힌트: {quiz.hint}")
                        point = 5
                    else:
                        print(" 이미 힌트를 보셨습니다.")
                    continue
                
                if user_str.isdigit() and 1 <= int(user_str) <= 4:
                    answer = int(user_str)
                    break
                else:
                    print(" 잘못된 입력입니다. 1-4 사이의 숫자나 'h'를 입력하세요.")
            
            if quiz.check_answer(answer):
                print(f" 정답입니다! (+{point}점)")
                score += point
            else:
                print(f" 오답입니다. (정답: {quiz.answer}번)")
            print("-" * 40)

        # 퍼센트 점수 대신 누적 합산 점수(score)로 관리 방식 변경
        print(f"\n========================================")
        print(f" 결과: {count}문제 중 총 획득 점수 {score}점!")
        
        if score > self.best_score:
            self.best_score = score
            print(" 새로운 최고 점수입니다!")
            self.save_data()
        print(f"========================================")
        
        #  [점수 기록 기능 추가 2] 파일에 이력 남기기
        self.save_history(count, score)

    def add_quiz(self):
        print("\n 새로운 퀴즈를 추가합니다.")
        question = input("문제를 입력하세요: ").strip()
        while not question:
            print(" 문제는 빈칸일 수 없습니다.")
            question = input("문제를 입력하세요: ").strip()

        choices = []
        for i in range(1, 5):
            choice = input(f"선택지 {i}: ").strip()
            while not choice:
                print(" 선택지는 빈칸일 수 없습니다.")
                choice = input(f"선택지 {i}: ").strip()
            choices.append(choice)

        answer = self.safe_input("정답 번호 (1-4): ", 1, 4)
        hint = input("힌트를 입력하세요: ").strip() #  힌트 입력 추가

        new_quiz = Quiz(question, choices, answer, hint)
        self.quizzes.append(new_quiz)
        self.save_data()
        print("\n 퀴즈가 성공적으로 추가되었습니다!")

    #  [삭제 기능 추가]
    def delete_quiz(self):
        self.show_list()
        if not self.quizzes:
            return
            
        delete_idx = self.safe_input("\n삭제할 퀴즈 번호를 선택하세요 (취소는 0): ", 0, len(self.quizzes))
        if delete_idx == 0:
            print(" 삭제를 취소합니다.")
            return
            
        del self.quizzes[delete_idx - 1]
        self.save_data()
        print(" 퀴즈가 성공적으로 삭제되었습니다!")

    def show_list(self):
        if not self.quizzes:
            print(" 등록된 퀴즈가 없습니다!")
            return
        print(f"\n 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for idx, quiz in enumerate(self.quizzes, 1):
            print(f"[{idx}] {quiz.question}")
        print("-" * 40)

    #  [점수 확인 기능 병합] 최고점과 모든 히스토리를 함께 보여줌
    def show_records(self):
        print(f"\n 역대 최고 점수: {self.best_score}점")
        print("-" * 40)
        print(" [모든 게임 기록]")
        try:
            with open("history.txt", "r", encoding="utf-8") as f:
                history = f.read().strip()
                if history:
                    print(history)
                else:
                    print(" 아직 게임 기록이 없습니다.")
        except FileNotFoundError:
            print(" 아직 게임 기록이 없습니다.")

    def run(self):
        while True:
            print("\n========================================")
            print("           나만의 퀴즈 게임          ")
            print("========================================")
            print("1. 퀴즈 풀기")
            print("2. 퀴즈 추가")
            print("3. 퀴즈 삭제") #  메뉴 재배치
            print("4. 퀴즈 목록")
            print("5. 점수/기록 확인")
            print("6. 종료")
            print("========================================")

            choice = self.safe_input("선택: ", 1, 6)

            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.delete_quiz()
            elif choice == 4:
                self.show_list()
            elif choice == 5:
                self.show_records() #  변경된 레코드 함수 호출
            elif choice == 6:
                self.save_data()
                print("프로그램을 종료합니다. 감사합니다! ")
                break


if __name__ == "__main__":
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\n 비정상 입력이 감지되어 프로그램을 안전하게 종료합니다.")
        game.save_data()
        sys.exit(0)