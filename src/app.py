import tkinter as tk
from pathlib import Path
from itertools import cycle
from PIL import Image, ImageTk


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Slideshow")
        self.geometry("800x400")
        self.fullscreen = False
        self.attributes("-fullscreen", self.fullscreen)
        self.configure(background='black', borderwidth=0, highlightthickness=0)
        self.update_idletasks()
        self.resizable(width=True, height=True)

        self.current_slide = tk.Label(self, borderwidth=0, highlightthickness=0)
        self.current_slide.pack()

        self.discarded = set()
        self.image_paths = set()
        self.images = cycle(self.image_paths)

        self.duration_ms = 3000

        # set up key binding
        self.bind("<Escape>",lambda e: self.destroy())
        self.bind("<Configure>", self.resize)
        self.bind("<Key-f>", self.toggle_fullscreen)

    def resize(self, event):
        pass

    def toggle_fullscreen(self, event):
        self.fullscreen = not self.fullscreen # toggle state
        self.config(cursor='none' if self.fullscreen else '')
        self.attributes("-fullscreen", self.fullscreen)

    def set_image_directory(self, path):
        from pathlib import Path
        self.image_dir = Path(path)
        self.update_images()

    def update_images(self):


        new_image_paths = set(self.image_dir.glob("*.jpg")) - self.discarded

        diff = new_image_paths - self.image_paths

        if diff or (not new_image_paths and self.image_paths):
            new_set = [p.name for p in diff] or 'empty'
            print(f'[image folder] new set: {new_set}')
            # new images were added
            self.images = cycle(diff)
            self.discarded.update(self.image_paths)
            self.image_paths = diff


        # self.images = cycle(zip(map(lambda p: p.name, image_paths), map(ImageTk.PhotoImage, map(Image.open, image_paths))))

    def load_image(self, image_path):
        image = Image.open(image_path)
        image = self.fit_image_to_current_size(image)
        return ImageTk.PhotoImage(image)

    def fit_image_to_current_size(self, image:Image) -> Image:
        w = self.winfo_width()
        h = self.winfo_height()
        w_img, h_img = image.size

        resize_mode = '-' if w_img > w or h_img > h else '+'
        print(f'[resize{resize_mode}] {Path(image.filename).name} from {w_img}x{h_img} to {w}x{h}')
        ratio = min(w/w_img, h/h_img)
        w_img = int(w_img*ratio)
        h_img = int(h_img*ratio)
        return image.resize((w_img,h_img), Image.LANCZOS)

    def display_next_slide(self):
        self.update_images()
        try:
            next_image_path = next(self.images)
            self.next_image = self.load_image(next_image_path)
            self.current_slide.config(image=self.next_image)
            self.title(next_image_path.name)
        except StopIteration:
            self.current_slide.config(image='', text=f'Add some images to \"{self.image_dir}\"', background='#000000', foreground='#ffffff', pady=10)

        self.after(self.duration_ms, self.display_next_slide)

    def start(self):
        self.display_next_slide()

def main():
    application = Application()
    # application.set_image_directory("/home/tmp/Downloads/photobox_test/")
    application.set_image_directory("/home/tmp/code/slideshow/test/no_images")
    application.start()
    application.mainloop()


if __name__ == "__main__":
    import sys
    sys.exit(main())
