import tkinter as tk


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Slideshow")
        self.geometry("800x400")
        self.fullscreen = False
        self.attributes("-fullscreen", self.fullscreen)
        self.configure(background='black', borderwidth=0, highlightthickness=0)
        self.center()
        self.resizable(width=True, height=True)
        self.current_slide = tk.Label(self, borderwidth=0, highlightthickness=0)
        self.current_slide.pack()
        self.duration_ms = 3000
        self.bind("<Escape>",lambda e: self.destroy())
        self.bind("<Key-f>", self.toggle_fullscreen)
        # self.bind("<Configure>", self.resize)

    # def resize(self, event):
    #     print("height", event.height, "width", event.width)

    def toggle_fullscreen(self, event):
        self.fullscreen = not self.fullscreen # toggle state
        self.attributes("-fullscreen", self.fullscreen)

    def set_image_directory(self, path):
        from pathlib import Path
        from itertools import cycle

        image_paths = Path(path).glob("*.jpg")
        # self.images = cycle(zip(map(lambda p: p.name, image_paths), map(ImageTk.PhotoImage, map(Image.open, image_paths))))
        self.images = cycle(image_paths)

    def load_image(self, image_path):
        from PIL import Image, ImageTk
        # w = self.winfo_screenwidth()
        # h = self.winfo_screenheight()
        w = self.winfo_width()
        h = self.winfo_height()

        pilImage = Image.open(image_path)
        imgWidth, imgHeight = pilImage.size
        if imgWidth > w or imgHeight > h:
            print(f'[resize] {image_path.name} from {imgWidth}x{imgHeight} to {w}x{h}')
            ratio = min(w/imgWidth, h/imgHeight)
            imgWidth = int(imgWidth*ratio)
            imgHeight = int(imgHeight*ratio)
            pilImage = pilImage.resize((imgWidth,imgHeight), Image.LANCZOS)
        return ImageTk.PhotoImage(pilImage)

    def center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        self.geometry(f"{w}x{h}")

    def display_next_slide(self):
        next_image_path = next(self.images)
        self.next_image = self.load_image(next_image_path)
        self.current_slide.config(image=self.next_image)
        self.title(next_image_path.name)
        self.center()
        self.after(self.duration_ms, self.display_next_slide)

    def start(self):
        self.display_next_slide()

def main():

    application = Application()
    # application.set_image_directory("/home/tmp/Downloads/photobox_test/")
    application.set_image_directory("/home/tmp/code/slideshow/test/images")
    application.start()
    application.mainloop()


if __name__ == "__main__":
    import sys
    sys.exit(main())
