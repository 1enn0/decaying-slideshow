import tkinter as tk
from pathlib import Path
from itertools import cycle
from PIL import Image, ImageTk, ImageOps
from collections import deque

import numpy as np
from lib import *

class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Paparazzi")
        self.geometry("800x400")
        self.fullscreen = False
        self.attributes("-fullscreen", self.fullscreen)
        self.configure(background='black')
        self.update_idletasks()
        self.resizable(width=True, height=True)

        self.current_slide = tk.Label(self, borderwidth=0, highlightthickness=0)
        self.current_slide.pack()

        self.img_catalog = list() # all images that we know of
        self.img_queue = deque() # new images that have not been shown

        self.remember_n_last_images = 2
        self.last_shown_images = []

        self.duration_ms = 5000

        # set up key binding
        self.bind("<Escape>",lambda e: self.destroy())
        # self.bind("<Configure>", self.resize)
        self.bind("<Key-f>", self.toggle_fullscreen)

    # def resize(self, event):
    #     pass

    def toggle_fullscreen(self, event):
        self.fullscreen = not self.fullscreen # toggle state
        self.config(cursor='none' if self.fullscreen else '')
        self.attributes("-fullscreen", self.fullscreen)

    def set_image_directory(self, path):
        from pathlib import Path
        self.image_dir = Path(path)

    def update_images(self):
        allowed_filetypes = ['*.jpg', '*.jpeg', '*.png', '*.tiff']
        all_images_in_dir = set()
        for ft in allowed_filetypes:
            all_images_in_dir.update(set([ImageEntry(p) for p in self.image_dir.glob(ft)]))
        all_known_images = set(self.img_catalog) | set(self.img_queue)
        new_images = all_images_in_dir - all_known_images

        # if there are new images, add them to the queue (ordered by age)
        if new_images:
            for img in sorted(new_images):
                self.img_queue.append(img)
            print(f'[update_images] {len(new_images)} new images, queue: {len(self.img_queue)}, catalog: {len(self.img_catalog)}')
        
    def load_image(self, image_path):
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
        image = self.fit_image_to_current_size(image)
        return ImageTk.PhotoImage(image)

    def fit_image_to_current_size(self, image:Image) -> Image:
        w = self.winfo_width()
        h = self.winfo_height()
        w_img, h_img = image.size

        resize_mode = '-' if w_img > w or h_img > h else '+'
        # print(f'[resize{resize_mode}] {Path(image.filename).name} from {w_img}x{h_img} to {w}x{h}')
        ratio = min(w/w_img, h/h_img)
        w_img = int(w_img*ratio)
        h_img = int(h_img*ratio)
        return image.resize((w_img,h_img), Image.LANCZOS)

    def display_next_slide(self):
        self.update_images()
        next_img_entry = None
        try:
            next_img_entry = self.img_queue.popleft() # newest image in queue
            self.img_catalog.append(next_img_entry)
            print(f'[display_next_slide]: showing {next_img_entry.name}, queue: {len(self.img_queue)}, catalog: {len(self.img_catalog)}')
        except IndexError: # queue is empty
            # show images from catalog if there are any
            if self.img_catalog:
                print(f'[display_next_slide]: queue empty, catalog: {len(self.img_catalog)}')
                reveal_counts = np.array([elt.num_reveals for elt in self.img_catalog])

                # get indices that would sort reveal_counts
                reveal_count_sort_idcs = np.argsort(reveal_counts)

                _, split_idcs = np.unique(reveal_counts[reveal_count_sort_idcs], return_index=True)

                # catalog_bucket_idcs is a list of arrays. Each array contains
                # indices into img_catalog for a group of elements that have been shown
                # the same number of times
                catalog_bucket_idcs = np.split(reveal_count_sort_idcs, split_idcs[1:])

                for idcs in catalog_bucket_idcs:
                    # and sort those by age
                    least_shown = sorted([self.img_catalog[i] for i in idcs])

                    for candidate in least_shown:
                        if candidate not in self.last_shown_images:
                            next_img_entry = candidate
                            break
                    
                    if next_img_entry is not None:
                        break


        if next_img_entry is not None:
            next_img_entry.increment_reveals()
            self.last_shown_images = [next_img_entry] + self.last_shown_images[:self.remember_n_last_images - 1]
            self.next_image = self.load_image(next_img_entry.path)
            self.current_slide.config(image=self.next_image)
            self.title(next_img_entry.name)
            print(f'num reveals in catalog: {[elt.num_reveals for elt in self.img_catalog]}')
        else:
            self.current_slide.config(image='', text=f'Add some images to \"{self.image_dir}\"', background='#000000', foreground='#ffffff', pady=10)
            print(f'[display_next_slide]: queue empty, catalog {len(self.img_catalog)}')


        self.after(self.duration_ms, self.display_next_slide)

    def start(self):
        self.display_next_slide()

def main():
    application = Application()
    application.set_image_directory("/home/tmp/Downloads/")
    application.start()
    application.mainloop()


if __name__ == "__main__":
    import sys
    sys.exit(main())
