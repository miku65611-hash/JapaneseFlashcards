import json
import os
import random
import shutil
from datetime import date, timedelta
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

STARTER = [
    {"word":"勉強","reading":"べんきょう","meaning":"Học tập","example":"日本語を勉強します。","level":"N5","category":"Học tập","known":False},
    {"word":"食べる","reading":"たべる","meaning":"Ăn","example":"ご飯を食べます。","level":"N5","category":"Ăn uống","known":False},
    {"word":"仕事","reading":"しごと","meaning":"Công việc","example":"仕事に行きます。","level":"N5","category":"Công việc","known":False},
    {"word":"大切","reading":"たいせつ","meaning":"Quan trọng","example":"家族は大切です。","level":"N4","category":"Cảm xúc & tính chất","known":False},
]
CATEGORIES = ["Khác","Đời sống","Học tập","Công việc","Ăn uống","Du lịch","Gia đình","Cảm xúc & tính chất","Thời gian","Mua sắm","Sức khỏe","Thiên nhiên"]

def today():
    return date.today().isoformat()

def make_button(text, callback, height=46):
    b = Button(text=text, size_hint_y=None, height=dp(height))
    b.bind(on_release=callback)
    return b

class FlashcardApp(App):
    def build(self):
        self.title = "Japanese Flashcards"
        self.words, self.index, self.revealed = [], 0, False
        self.dark = False
        self.load_words()
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        self.header = Label(text="[b]日本語 FLASHCARDS[/b]\\nHọc từ vựng tiếng Nhật", markup=True,
                            size_hint_y=None, height=dp(58), font_size="19sp")
        self.root_box.add_widget(self.header)
        nav = GridLayout(cols=4, size_hint_y=None, height=dp(44), spacing=dp(4))
        for title, fn in [
            ("HỌC", self.show_study), ("ÔN TẬP", self.show_review),
            ("KIỂM TRA", self.show_quiz), ("THÊM TỪ", self.show_add),
        ]:
            nav.add_widget(make_button(title, lambda _, f=fn: f(), 44))
        self.root_box.add_widget(nav)
        nav2 = GridLayout(cols=4, size_hint_y=None, height=dp(42), spacing=dp(4))
        for title, fn in [
            ("DANH SÁCH", self.show_list), ("THỐNG KÊ", self.show_stats),
            ("SAO LƯU", self.backup), ("GIAO DIỆN", self.toggle_theme),
        ]:
            nav2.add_widget(make_button(title, lambda _, f=fn: f(), 42))
        self.root_box.add_widget(nav2)
        self.content = BoxLayout(orientation="vertical", spacing=dp(7))
        self.root_box.add_widget(self.content)
        self.apply_theme()
        self.show_study()
        return self.root_box

    def data_path(self):
        return os.path.join(self.user_data_dir, "vocabulary.json")

    def load_words(self):
        try:
            with open(self.data_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.words = data if isinstance(data, list) else [dict(x) for x in STARTER]
        except (OSError, ValueError, TypeError):
            self.words = [dict(x) for x in STARTER]
            self.save_words()
        for w in self.words:
            w.setdefault("category", "Khác")
            w.setdefault("known", False)
            w.setdefault("interval", 0)
            w.setdefault("streak", 0)
            w.setdefault("due", today())
            w.setdefault("reviews", 0)

    def save_words(self):
        os.makedirs(self.user_data_dir, exist_ok=True)
        temp = self.data_path() + ".tmp"
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(self.words, f, ensure_ascii=False, indent=2)
        os.replace(temp, self.data_path())

    def set_content(self, widget):
        self.content.clear_widgets()
        self.content.add_widget(widget)

    def label(self, text, **kwargs):
        color = kwargs.pop("color", self.fg)
        return Label(text=text, color=color, **kwargs)

    def stats_label(self):
        known = sum(bool(w.get("known")) for w in self.words)
        due = sum(w.get("due", today()) <= today() for w in self.words)
        return self.label(f"Tổng: {len(self.words)}   Đã thuộc: {known}   Cần ôn: {due}",
                          size_hint_y=None, height=dp(32), font_size="14sp")

    def apply_theme(self):
        self.bg = (0.08,0.09,0.12,1) if self.dark else (0.96,0.97,0.99,1)
        self.fg = (0.94,0.95,0.98,1) if self.dark else (0.12,0.14,0.18,1)
        self.root_box.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with self.root_box.canvas.before:
            Color(*self.bg)
            self._bg_rect = Rectangle(pos=self.root_box.pos, size=self.root_box.size)
        self.root_box.bind(pos=self._update_bg, size=self._update_bg)
        for w in self.root_box.walk():
            if isinstance(w, Label):
                w.color = self.fg

    def _update_bg(self, *_):
        if hasattr(self, "_bg_rect"):
            self._bg_rect.pos = self.root_box.pos
            self._bg_rect.size = self.root_box.size

    def toggle_theme(self, *_):
        self.dark = not self.dark
        self.apply_theme()
        self.show_study()
        self.message("Giao diện", "Đã chuyển sang " + ("Dark Mode." if self.dark else "giao diện sáng."))

    def show_study(self):
        box = BoxLayout(orientation="vertical", spacing=dp(8))
        box.add_widget(self.stats_label())
        if not self.words:
            box.add_widget(self.label("Chưa có từ vựng. Hãy thêm từ mới!"))
            self.set_content(box); return
        self.index %= len(self.words)
        w = self.words[self.index]
        box.add_widget(self.label(f"Thẻ {self.index+1} / {len(self.words)} · {w.get('category','Khác')}",
                                  size_hint_y=None, height=dp(26)))
        card = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        card.add_widget(self.label(f"[b]{w.get('word','')}[/b]", markup=True, font_size="38sp"))
        card.add_widget(self.label(w.get("reading",""), font_size="23sp"))
        if self.revealed:
            card.add_widget(self.label(f"[b]{w.get('meaning','')}[/b]", markup=True, font_size="24sp"))
            card.add_widget(self.label(w.get("example",""), font_size="16sp"))
            card.add_widget(self.label(f"JLPT: {w.get('level','N5')} · Chủ đề: {w.get('category','Khác')}"))
        else:
            card.add_widget(self.label("Chạm XEM NGHĨA để tự kiểm tra", color=(0.5,0.5,0.5,1)))
        box.add_widget(card)
        row = GridLayout(cols=2, size_hint_y=None, height=dp(45), spacing=dp(5))
        row.add_widget(make_button("🔊 NGHE PHÁT ÂM", lambda *_: self.speak(w.get("word",""))))
        row.add_widget(make_button("XEM NGHĨA" if not self.revealed else "ẨN NGHĨA", self.toggle_reveal))
        box.add_widget(row)
        row = GridLayout(cols=3, size_hint_y=None, height=dp(44), spacing=dp(5))
        row.add_widget(make_button("← Trước", self.previous))
        row.add_widget(make_button("Tiếp →", self.next))
        row.add_widget(make_button("Trộn 🔀", self.shuffle))
        box.add_widget(row)
        row = GridLayout(cols=2, size_hint_y=None, height=dp(44), spacing=dp(5))
        row.add_widget(make_button("✕ Chưa thuộc", lambda *_: self.mark(False)))
        row.add_widget(make_button("✓ Đã thuộc", lambda *_: self.mark(True)))
        box.add_widget(row)
        self.set_content(box)

    def speak(self, text):
        if not text:
            self.message("Phát âm", "Từ này chưa có nội dung để đọc."); return
        try:
            if platform == "android":
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
                Locale = autoclass("java.util.Locale")
                if not hasattr(self, "_tts"):
                    from jnius import PythonJavaClass, java_method
                    app = self
                    class InitListener(PythonJavaClass):
                        __javainterfaces__ = ["android/speech/tts/TextToSpeech$OnInitListener"]
                        __javacontext__ = "app"
                        @java_method("(I)V")
                        def onInit(self, status):
                            if status == TextToSpeech.SUCCESS:
                                app._tts.setLanguage(Locale.JAPANESE)
                                app._tts_ready = True
                    self._tts_ready = False
                    self._tts_listener = InitListener()
                    self._tts = TextToSpeech(PythonActivity.mActivity, self._tts_listener)
                if self._tts_ready:
                    self._tts.speak(text, TextToSpeech.QUEUE_FLUSH, None)
                else:
                    self.message("Phát âm", "Bộ đọc tiếng Nhật đang khởi động. Hãy thử lại sau giây lát.")
            else:
                try:
                    import pyttsx3
                    if not hasattr(self, "_engine"):
                        self._engine = pyttsx3.init()
                        voices = self._engine.getProperty("voices")
                        for v in voices:
                            if "japan" in (v.id + v.name).lower():
                                self._engine.setProperty("voice", v.id); break
                    self._engine.say(text); self._engine.runAndWait()
                except ImportError:
                    self.message("Phát âm", "Máy tính cần cài pyttsx3 và giọng đọc tiếng Nhật. Android dùng TTS hệ thống.")
        except Exception as e:
            self.message("Phát âm", "Không khởi động được TTS. Hãy cài giọng tiếng Nhật ngoại tuyến trong cài đặt thiết bị.")

    def toggle_reveal(self, *_):
        self.revealed = not self.revealed; self.show_study()
    def previous(self, *_):
        if self.words: self.index=(self.index-1)%len(self.words); self.revealed=False
        self.show_study()
    def next(self, *_):
        if self.words: self.index=(self.index+1)%len(self.words); self.revealed=False
        self.show_study()
    def shuffle(self, *_):
        if self.words: self.index=random.randrange(len(self.words)); self.revealed=False
        self.show_study()

    def mark(self, known):
        if self.words:
            w=self.words[self.index]
            w["known"]=known
            self.record_review(w, known)
            self.save_words()
            self.index=(self.index+1)%len(self.words); self.revealed=False
        self.show_study()

    def record_review(self, w, correct):
        w["reviews"]=w.get("reviews",0)+1
        if correct:
            w["streak"]=w.get("streak",0)+1
            old=max(0,int(w.get("interval",0)))
            w["interval"] = 1 if old == 0 else min(60, max(2, round(old*2.2)))
            w["due"]=(date.today()+timedelta(days=w["interval"])).isoformat()
        else:
            w["streak"]=0; w["interval"]=0; w["due"]=today()

    def show_add(self):
        box=BoxLayout(orientation="vertical",spacing=dp(6))
        box.add_widget(self.label("[b]THÊM TỪ VỰNG MỚI[/b]",markup=True,size_hint_y=None,height=dp(32)))
        fields={}
        for key,hint in [("word","Từ tiếng Nhật (bắt buộc)"),("reading","Cách đọc Hiragana / Katakana"),("meaning","Nghĩa tiếng Việt (bắt buộc)"),("example","Ví dụ / ghi chú")]:
            inp=TextInput(hint_text=hint,multiline=False,size_hint_y=None,height=dp(43))
            fields[key]=inp; box.add_widget(inp)
        row=GridLayout(cols=2,size_hint_y=None,height=dp(44),spacing=dp(5))
        level=Spinner(text="N5",values=("N5","N4","N3","N2","N1","Khác"))
        category=Spinner(text="Khác",values=tuple(CATEGORIES))
        row.add_widget(level); row.add_widget(category); box.add_widget(row)
        def save_new(*_):
            word,meaning=fields["word"].text.strip(),fields["meaning"].text.strip()
            if not word or not meaning:
                self.message("Thiếu thông tin","Cần nhập từ tiếng Nhật và nghĩa tiếng Việt."); return
            self.words.append({"word":word,"reading":fields["reading"].text.strip(),"meaning":meaning,
                "example":fields["example"].text.strip(),"level":level.text,"category":category.text,
                "known":False,"interval":0,"streak":0,"due":today(),"reviews":0})
            self.save_words(); self.index=len(self.words)-1; self.revealed=False; self.show_study()
        box.add_widget(make_button("LƯU TỪ VỰNG",save_new))
        self.set_content(box)

    def show_list(self):
        outer=BoxLayout(orientation="vertical",spacing=dp(5))
        outer.add_widget(self.stats_label())
        search=TextInput(hint_text="Tìm từ hoặc nghĩa...",multiline=False,size_hint_y=None,height=dp(42))
        outer.add_widget(search)
        cat=Spinner(text="Tất cả chủ đề",values=("Tất cả chủ đề",)+tuple(CATEGORIES),size_hint_y=None,height=dp(42))
        outer.add_widget(cat)
        scroll=ScrollView(); listing=GridLayout(cols=1,spacing=dp(5),size_hint_y=None,padding=dp(2))
        listing.bind(minimum_height=listing.setter("height")); scroll.add_widget(listing); outer.add_widget(scroll)
        def refresh(*_):
            listing.clear_widgets(); q=search.text.casefold().strip()
            for i,w in enumerate(self.words):
                s=f"{w.get('word','')} ({w.get('reading','')})\\n{w.get('meaning','')} · {w.get('level','')} · {w.get('category','Khác')}"
                if q and q not in s.casefold(): continue
                if cat.text!="Tất cả chủ đề" and w.get("category","Khác")!=cat.text: continue
                row=BoxLayout(size_hint_y=None,height=dp(68),spacing=dp(4))
                row.add_widget(self.label(s,halign="left",valign="middle"))
                row.add_widget(make_button("Học",lambda _,n=i:self.open_card(n),42))
                row.add_widget(make_button("Xóa",lambda _,n=i:self.delete_word(n),42))
                listing.add_widget(row)
        search.bind(text=refresh); cat.bind(text=refresh); refresh(); self.set_content(outer)

    def open_card(self,i):
        self.index=i; self.revealed=False; self.show_study()
    def delete_word(self,i):
        self.words.pop(i); self.save_words(); self.index=min(self.index,max(0,len(self.words)-1)); self.show_list()

    def show_review(self):
        due=[(i,w) for i,w in enumerate(self.words) if w.get("due",today())<=today()]
        box=BoxLayout(orientation="vertical",spacing=dp(8))
        box.add_widget(self.label(f"[b]ÔN TẬP THÔNG MINH[/b]\\nĐến hạn hôm nay: {len(due)} từ",markup=True,
                                  size_hint_y=None,height=dp(55)))
        box.add_widget(self.label("Từ trả lời đúng sẽ được giãn thời gian ôn. Từ sai sẽ quay lại hôm nay.",
                                  size_hint_y=None,height=dp(45),font_size="14sp"))
        if due:
            def start(*_):
                self.review_queue=[i for i,_ in due]; self.review_pos=0; self.review_next()
            box.add_widget(make_button("BẮT ĐẦU ÔN TẬP",start))
            for _,w in due[:8]:
                box.add_widget(self.label(f"• {w.get('word')}  ·  {w.get('category','Khác')}"))
        else:
            box.add_widget(self.label("Bạn đã ôn hết từ đến hạn. Quá hiếm hoi, hãy tận hưởng."))
        self.set_content(box)

    def review_next(self):
        if self.review_pos>=len(self.review_queue):
            self.save_words(); self.message("Hoàn thành","Bạn đã hoàn thành lượt ôn tập."); self.show_review(); return
        i=self.review_queue[self.review_pos]
        if i>=len(self.words): self.review_pos+=1; self.review_next(); return
        self.index=i; self.revealed=False
        w=self.words[i]
        box=BoxLayout(orientation="vertical",spacing=dp(9))
        box.add_widget(self.label(f"Ôn tập {self.review_pos+1}/{len(self.review_queue)}",size_hint_y=None,height=dp(30)))
        box.add_widget(self.label(f"[b]{w.get('word')}[/b]",markup=True,font_size="38sp"))
        box.add_widget(self.label(w.get("reading",""),font_size="22sp"))
        box.add_widget(make_button("🔊 NGHE PHÁT ÂM",lambda *_:self.speak(w.get("word",""))))
        box.add_widget(make_button("HIỆN NGHĨA",lambda *_:self.review_answer(w)))
        self.set_content(box)

    def review_answer(self,w):
        box=BoxLayout(orientation="vertical",spacing=dp(8))
        box.add_widget(self.label(f"[b]{w.get('meaning')}[/b]\\n{w.get('example','')}",markup=True,font_size="20sp"))
        row=GridLayout(cols=2,size_hint_y=None,height=dp(48),spacing=dp(5))
        def answer(ok):
            self.record_review(w,ok); self.review_pos+=1; self.review_next()
        row.add_widget(make_button("✕ Chưa nhớ",lambda *_:answer(False)))
        row.add_widget(make_button("✓ Đã nhớ",lambda *_:answer(True)))
        box.add_widget(row); self.set_content(box)

    def show_quiz(self):
        box=BoxLayout(orientation="vertical",spacing=dp(8))
        box.add_widget(self.label("[b]KIỂM TRA TRẮC NGHIỆM[/b]",markup=True,size_hint_y=None,height=dp(38)))
        if len(self.words)<2:
            box.add_widget(self.label("Cần ít nhất 2 từ để tạo câu hỏi trắc nghiệm.")); self.set_content(box); return
        box.add_widget(self.label("Chọn đáp án đúng cho từ tiếng Nhật.",size_hint_y=None,height=dp(30)))
        box.add_widget(make_button("BẮT ĐẦU BÀI KIỂM TRA",self.start_quiz))
        self.set_content(box)

    def start_quiz(self,*_):
        self.quiz_items=random.sample(self.words,min(10,len(self.words)))
        self.quiz_pos=0; self.quiz_score=0; self.quiz_question()

    def quiz_question(self):
        if self.quiz_pos>=len(self.quiz_items):
            box=BoxLayout(orientation="vertical",spacing=dp(10))
            box.add_widget(self.label(f"[b]KẾT QUẢ: {self.quiz_score}/{len(self.quiz_items)}[/b]",markup=True,font_size="28sp"))
            box.add_widget(self.label(f"Đúng {round(self.quiz_score/len(self.quiz_items)*100)}%"))
            box.add_widget(make_button("LÀM LẠI",self.start_quiz))
            box.add_widget(make_button("VỀ KIỂM TRA",self.show_quiz))
            self.set_content(box); return
        w=self.quiz_items[self.quiz_pos]
        others=[x for x in self.words if x is not w]
        choices=[w]+random.sample(others,min(3,len(others)))
        random.shuffle(choices); self.quiz_answered=False
        box=BoxLayout(orientation="vertical",spacing=dp(8))
        box.add_widget(self.label(f"Câu {self.quiz_pos+1}/{len(self.quiz_items)} · Điểm {self.quiz_score}",
                                  size_hint_y=None,height=dp(30)))
        box.add_widget(self.label(f"[b]{w.get('word')}[/b]",markup=True,font_size="38sp"))
        box.add_widget(self.label(w.get("reading",""),font_size="21sp"))
        for c in choices:
            box.add_widget(make_button(c.get("meaning",""),lambda _,choice=c:self.check_quiz(w,choice)))
        self.set_content(box)

    def check_quiz(self,w,choice):
        if self.quiz_answered:return
        self.quiz_answered=True
        correct=choice is w
        if correct:self.quiz_score+=1
        self.record_review(w,correct); self.save_words()
        self.message("Kết quả",("Chính xác!" if correct else f"Chưa đúng. Đáp án: {w.get('meaning')}"))
        self.quiz_pos+=1
        Clock.schedule_once(lambda *_:self.quiz_question(),0.25)

    def show_stats(self):
        total=len(self.words); known=sum(bool(w.get("known")) for w in self.words)
        due=sum(w.get("due",today())<=today() for w in self.words)
        reviewed=sum(int(w.get("reviews",0)) for w in self.words)
        box=BoxLayout(orientation="vertical",spacing=dp(9))
        box.add_widget(self.label("[b]THỐNG KÊ TIẾN ĐỘ HỌC[/b]",markup=True,font_size="21sp"))
        for line in [f"Tổng số từ: {total}",f"Đã đánh dấu thuộc: {known}",
                     f"Chưa thuộc: {total-known}",f"Từ đến hạn ôn: {due}",
                     f"Tổng lượt ôn/kiểm tra: {reviewed}",
                     f"Tỷ lệ đã thuộc: {round(known/total*100) if total else 0}%"]:
            box.add_widget(self.label(line,size_hint_y=None,height=dp(35)))
        box.add_widget(self.label("[b]Theo chủ đề[/b]",markup=True))
        counts={}
        for w in self.words: counts[w.get("category","Khác")]=counts.get(w.get("category","Khác"),0)+1
        for cat,n in sorted(counts.items()):
            box.add_widget(self.label(f"{cat}: {n} từ",size_hint_y=None,height=dp(28)))
        self.set_content(box)

    def backup(self,*_):
        os.makedirs(self.user_data_dir,exist_ok=True)
        path=os.path.join(self.user_data_dir,"JapaneseFlashcards_backup.json")
        with open(path,"w",encoding="utf-8") as f:
            json.dump({"format":"JapaneseFlashcards","version":2,"words":self.words},
                      f,ensure_ascii=False,indent=2)
        box=BoxLayout(orientation="vertical",spacing=dp(8),padding=dp(8))
        box.add_widget(self.label("Đã tạo bản sao lưu trong thư mục dữ liệu ứng dụng:",size_hint_y=None,height=dp(42)))
        path_input=TextInput(text=path,multiline=True,readonly=True,size_hint_y=None,height=dp(80))
        box.add_widget(path_input)
        box.add_widget(make_button("CHỌN FILE ĐỂ KHÔI PHỤC",lambda *_:self.restore_picker()))
        box.add_widget(make_button("ĐÓNG",lambda *_:self._popup.dismiss()))
        self._popup=Popup(title="Sao lưu dữ liệu",content=box,size_hint=(0.92,0.55)); self._popup.open()

    def restore_picker(self):
        chooser=FileChooserListView(path=os.path.expanduser("~"),filters=["*.json"])
        layout=BoxLayout(orientation="vertical",spacing=dp(5))
        layout.add_widget(chooser)
        row=GridLayout(cols=2,size_hint_y=None,height=dp(44),spacing=dp(5))
        pop=Popup(title="Chọn file sao lưu JSON",content=layout,size_hint=(0.95,0.85))
        def restore(*_):
            if not chooser.selection:
                self.message("Khôi phục","Hãy chọn một file JSON."); return
            try:
                with open(chooser.selection[0],"r",encoding="utf-8") as f:data=json.load(f)
                words=data.get("words") if isinstance(data,dict) else data
                if not isinstance(words,list) or any(not isinstance(x,dict) or "word" not in x or "meaning" not in x for x in words):
                    raise ValueError("Định dạng dữ liệu không hợp lệ")
                self.words=words
                for w in self.words:
                    w.setdefault("category","Khác");w.setdefault("known",False);w.setdefault("due",today())
                    w.setdefault("interval",0);w.setdefault("streak",0);w.setdefault("reviews",0)
                self.save_words();self.index=0;self.show_study();pop.dismiss()
                self.message("Khôi phục","Đã khôi phục dữ liệu thành công.")
            except Exception as e:self.message("Lỗi khôi phục",str(e))
        row.add_widget(make_button("KHÔI PHỤC",restore))
        row.add_widget(make_button("HỦY",lambda *_:pop.dismiss()))
        layout.add_widget(row);pop.open()

    def message(self,title,message):
        Popup(title=title,content=Label(text=message),size_hint=(0.88,0.38)).open()

if __name__=="__main__":
    FlashcardApp().run()
