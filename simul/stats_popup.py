import tkinter as tk

class StatsPopup:
    def __init__(self, sim):
        self.sim = sim
        self.root = tk.Tk()
        self.root.title("교통 통계")
        self.root.geometry("420x340+700+100")
        self.root.resizable(False, False)
        self.labels = []
        for i in range(12):
            lbl = tk.Label(self.root, text="", font=("맑은 고딕", 17), anchor="w", fg="#205090", bg="#F6FAFF")
            lbl.pack(fill=tk.X, padx=14, pady=2)
            self.labels.append(lbl)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.root.destroy()

    def run(self):
        self.update_stats()
        self.root.mainloop()

    def update_stats(self):
        stats = self.sim.get_live_stats()
        kor_stats = [self._translate(s) for s in stats]
        for i in range(len(self.labels)):
            self.labels[i].config(text=kor_stats[i] if i < len(kor_stats) else "")
        self.root.after(1000, self.update_stats)  # 1초마다 갱신

    def _translate(self, s):
        d = {
            "[Live Traffic Stats]": "[실시간 교통 통계]",
            "Arrived vehicles:": "도착 차량:",
            "Average travel time:": "평균 이동시간:",
            "Average speed:": "평균 속도:",
            "Min:": "최소:",
            "Max:": "최대:",
            "Congestion by cell:": "셀별 혼잡도:",
            "Average congestion:": "평균 혼잡도:",
            "(Press SPACE to show/save results)": "(스페이스바로 결과표/저장)"
        }
        for eng, kor in d.items():
            s = s.replace(eng, kor)
        return s