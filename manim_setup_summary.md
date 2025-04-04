# Manim and Manim Slides Setup Summary

**Note:** This setup process has been verified to work in a standard GitHub Codespace environment, although the interactive presenter (`manim-slides SceneName`) requires a graphical display which is typically unavailable in Codespaces. Use the `convert` command instead (Options B or C below) to generate HTML or PPTX files that can be viewed locally.

This document summarizes the commands needed to install `manim` and `manim-slides` and handle the dependencies encountered in a typical Linux environment (like the one used in our session).

## 1. Install System Dependencies

These libraries are required for `manim`, `manim-slides`, and the underlying graphics/UI frameworks (Cairo, Pango, Qt, OpenGL).

```bash
sudo apt update && sudo apt install -y libcairo2-dev libpango1.0-dev pkg-config libgl1-mesa-glx libegl1-mesa libpulse0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0
```

## 2. Install Python Packages

Install `manim` and `manim-slides` using pip.

```bash
pip install manim manim-slides
```

## 3. Create your Manim Slides Python file

Write your presentation code in a Python file (e.g., `my_presentation.py`). Ensure your scene class inherits from `manim_slides.Slide` and use `self.next_slide()` to define slide breaks.

*(Example from our session: `slides_example.py`)*

## 4. Render the Slides

Use the `manim-slides render` command to process your Python file and generate the necessary video/image assets for the presentation. Replace `<your_script.py>` and `<YourSlideSceneName>` with your actual file and scene name.

```bash
manim-slides render <your_script.py> <YourSlideSceneName>
```

*(Example from our session: `manim-slides render slides_example.py BasicExample`)*

## 5. Present or Convert

Choose one of the following options:

### Option A: Attempt to Present (Requires GUI)

If you are in an environment with a graphical display server (like a standard desktop), you can try to launch the interactive presenter:

```bash
manim-slides <YourSlideSceneName>
```

*(Note: This failed in our session with a "could not connect to display" error due to the lack of a graphical environment like in a standard GitHub Codespace.)*

### Option B: Convert to HTML (No GUI needed)

If the presenter fails or you prefer a file-based format, convert to a self-contained HTML file:

```bash
manim-slides convert --to html --one-file <YourSlideSceneName> <output_name.html>
```

*(Example from our session: `manim-slides convert --to html --one-file BasicExample basic_example.html`)*

### Option C: Convert to PPTX (No GUI needed)

Alternatively, convert to a PowerPoint file:

```bash
manim-slides convert --to pptx <YourSlideSceneName> <output_name.pptx>
```

*(Example from our session: `manim-slides convert --to pptx BasicExample basic_example.pptx`)*