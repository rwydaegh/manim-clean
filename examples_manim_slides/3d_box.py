from manim import *
from manim_slides import Slide
import matplotlib.pyplot as plt

class WireframeBoxWithSlice(ThreeDScene, Slide):
    def construct(self):
        # Create a wireframe box
        X_size, Y_size, Z_size = 3, 3, 3
        box = Prism(dimensions=[X_size, Y_size, Z_size])
        box.set_opacity(0.5)
        box.set_stroke(color=WHITE, width=1)

        # Add dotted lines which slice through the box at the hotspot location
        hotspot_location = [X_size/4, Y_size/4, Z_size/4]
        line1 = Line(start=[hotspot_location[0], hotspot_location[1], -Z_size], end=[hotspot_location[0], hotspot_location[1], Z_size], color=RED)
        line2 = Line(start=[-X_size, hotspot_location[1], -hotspot_location[2]], end=[X_size, hotspot_location[1], -hotspot_location[2]], color=GREEN)
        line3 = Line(start=[hotspot_location[0], -Y_size, -hotspot_location[2]], end=[hotspot_location[0], Y_size, -hotspot_location[2]], color=BLUE)
        line1.rotate(PI/6, axis=RIGHT, about_point=box.get_center())
        line2.rotate(PI/6, axis=RIGHT, about_point=box.get_center())
        line3.rotate(PI/6, axis=RIGHT, about_point=box.get_center())
        line1.rotate(PI/24, axis=UP, about_point=box.get_center())
        line2.rotate(PI/24, axis=UP, about_point=box.get_center())
        line3.rotate(PI/24, axis=UP, about_point=box.get_center())
        
        # Rotate the box
        box.rotate(PI/6, axis=RIGHT)
        box.rotate(PI/24, axis=UP)

        # Add the box to the scene
        self.add(box)
        
        # Animate creation of the box
        self.play(Create(box), run_time=1)

        self.wait(0.5)
        self.next_slide()
        
        # Create a full rectangle that will slice through the box horizontally
        rectangle = Rectangle(width=X_size * 1.3, height=Z_size * 1.3).set_fill(RED, opacity=0.7)
        rectangle.set_stroke(width=0)
        rectangle.rotate(PI/2, axis=RIGHT, about_point=box.get_center())
        rectangle.rotate(PI/6, axis=RIGHT, about_point=box.get_center())
        rectangle.rotate(PI/24, axis=UP, about_point=box.get_center())
        rectangle.shift(4 * LEFT)

        self.play(FadeIn(rectangle), run_time=1)
        self.play(rectangle.animate.shift(4 * RIGHT), run_time=1)

        self.wait(0.5)
        self.next_slide()

        # Rotate back to original position
        rerotate = AnimationGroup(
            Rotate(box, angle=-PI/24, axis=UP),
            Rotate(rectangle, angle=-PI/24, axis=UP, about_point=box.get_center())
        )
        line1.rotate(-PI/24, axis=UP, about_point=box.get_center())
        line2.rotate(-PI/24, axis=UP, about_point=box.get_center())
        line3.rotate(-PI/24, axis=UP, about_point=box.get_center())
        self.play(rerotate, run_time=1)

        rerotate = AnimationGroup(
            Rotate(box, angle=-PI/6+PI/2, axis=RIGHT),
            Rotate(rectangle, angle=-PI/6+PI/2, axis=RIGHT, about_point=box.get_center())
        )
        line1.rotate(-PI/6+PI/2, axis=RIGHT, about_point=box.get_center())
        line2.rotate(-PI/6+PI/2, axis=RIGHT, about_point=box.get_center())
        line3.rotate(-PI/6+PI/2, axis=RIGHT, about_point=box.get_center())
        self.play(rerotate, run_time=1)
        
        self.wait(0.5)
        self.next_slide()

        # Move camera to orthographic view
        default_focal_distance = self.renderer.camera.get_focal_distance()
        self.move_camera(focal_distance=100)

        # animate rectangle to white color
        rect_color = ApplyMethod(rectangle.set_fill, WHITE, 1)

        # Add 2D colorplot in the cube
        x = np.linspace(-X_size/2, X_size/2, 100)
        z = np.linspace(-Z_size/2, Z_size/2, 100)
        X, Z = np.meshgrid(x, z)
        Y = (1+5*np.exp(-((X - hotspot_location[0])**2 / 0.1 + (Z - hotspot_location[1])**2 / 0.2) ) ) * np.cos(2 * np.pi * np.sqrt((X - hotspot_location[0])**2 + (Z - hotspot_location[1])**2) / 0.3)
        fig = plt.figure(figsize=(X_size, Z_size))
        ax = fig.add_subplot(111)
        ax.contourf(X, Z, Y, 100, cmap='jet')
        ax.axis('off')
        plt.gca().set_position([0, 0, 1, 1])
        plt.savefig('colorplot.png')
        plt.close()

        # Add the colorplot to the scene
        colorplot = ImageMobject('colorplot.png')
        colorplot.set_width(X_size)
        colorplot.set_height(Z_size)
        # move the colorplot to the hotspot location
        move = box.get_center() + hotspot_location
        colorplot.move_to([0, 0, move[2]])
        colorplot.set_opacity(0.7)
        self.add(colorplot)

        # Make the colorplot appear in the box
        colorplot_fadein = FadeIn(colorplot)
        self.play(rect_color, colorplot_fadein, run_time=1)

        self.wait(0.5)
        self.next_slide()

        # Add a dot at the hotspot location
        hotspot = Sphere(radius=0.09, color=WHITE).move_to(hotspot_location)
        hotspot.set_color(WHITE)
        hotspot.set_stroke(width=0)
        hotspot_label = Tex("Hotspot").next_to(hotspot, RIGHT + UP)

        # Animate both
        box.set_fill(color=WHITE, opacity=0)
        box.set_stroke(color=WHITE, width=2, opacity=1)
        self.add(hotspot)
        self.add(hotspot_label)
        self.remove(rectangle)
        # make animation that reduces the box opacity to 0.7
        self.play(FadeIn(hotspot), Write(hotspot_label), run_time=1)

        self.wait(0.5)
        self.next_slide()

        # Animate the dotted lines
        # Create line labels
        line1_label = MathTex("x").next_to(line1.get_end(), RIGHT).set_color(RED)
        line2_label = MathTex("y").next_to(line2.get_end(), UP).set_color(GREEN)
        self.play(Create(line1), Create(line2), Write(line1_label), Write(line2_label), run_time=1)
        self.add(line1)
        self.add(line2)

        # Zoom out, reset focal length to normal, and go back to 3D perspective by rotating everything back
        self.play(FadeOut(hotspot_label), run_time=1)
        self.remove(hotspot_label, colorplot)
        self.move_camera(focal_distance=default_focal_distance, run_time=1)
        rerotate = AnimationGroup(
            Rotate(box, angle=PI/6-PI/2, axis=RIGHT),
            Rotate(line1, angle=PI/6-PI/2, axis=RIGHT, about_point=box.get_center()),
            Rotate(line2, angle=PI/6-PI/2, axis=RIGHT, about_point=box.get_center()),
            Rotate(hotspot, angle=PI/6-PI/2, axis=RIGHT, about_point=box.get_center()),
            Rotate(line1_label, angle=PI/6-PI/2, axis=RIGHT, about_point=box.get_center()),
            Rotate(line2_label, angle=PI/6-PI/2, axis=RIGHT, about_point=box.get_center())
            #Rotate(hotspot_label, angle=PI/6-PI/2, axis=RIGHT, about_point=box.get_center()),
            #Rotate(colorplot, angle=PI/6-PI/2, axis=RIGHT, about_point=box.get_center())
        )
        line3.rotate(PI/6-PI/2, axis=RIGHT, about_point=box.get_center())
        self.play(rerotate, run_time=1)

        rerotate = AnimationGroup(
            Rotate(box, angle=PI/12, axis=UP),
            Rotate(line1, angle=PI/12, axis=UP, about_point=box.get_center()),
            Rotate(line2, angle=PI/12, axis=UP, about_point=box.get_center()),
            Rotate(hotspot, angle=PI/12, axis=UP, about_point=box.get_center()),
            Rotate(line1_label, angle=PI/12, axis=UP, about_point=box.get_center()),
            Rotate(line2_label, angle=PI/12, axis=UP, about_point=box.get_center())
            #Rotate(hotspot_label, angle=PI/12, axis=UP, about_point=box.get_center()),
            #Rotate(colorplot, angle=PI/12, axis=UP, about_point=box.get_center())
        )
        line3.rotate(PI/12, axis=UP, about_point=box.get_center())
        self.play(rerotate, run_time=1)

        # Show third line
        line3_label = MathTex("z").next_to(line3.get_end(), UP).set_color(BLUE)
        # transform the lines into arrows
        arrow1 = Arrow(start=line1.get_start(), end=line1.get_end()).set_color(RED)
        arrow2 = Arrow(start=line2.get_start(), end=line2.get_end()).set_color(GREEN)
        arrow3 = Arrow(start=line3.get_start(), end=line3.get_end()).set_color(BLUE)
        self.play(Write(line3_label), ReplacementTransform(line1, arrow1), ReplacementTransform(line2, arrow2), ReplacementTransform(line3, arrow3), run_time=1)
        self.add(arrow3)

        self.wait(0.5)
        self.next_slide()

        # Shift everything to the left
        objects_3d = VGroup(box, arrow1, arrow2, arrow3, hotspot, line1_label, line2_label, line3_label)
        self.play(objects_3d.animate.shift(3 * LEFT), run_time=1)

        # Function to create a graph using Manim
        def create_graph(axis_label, axis_color, x_data, y_func):
            y_data = y_func(x_data)
            # normalize the y_data
            max_y = np.max(y_data)*3
            y_data = y_data / max_y
            axes = Axes(
                x_range=[np.min(x_data), np.max(x_data), 1],
                y_range=[np.min(y_data), np.max(y_data), 1],
                axis_config={
                    "include_tip": True,
                    "include_numbers": True,
                    "color": WHITE
                },
                # dont include 0 in the y axis
                y_axis_config={"include_numbers": False}
            )
            graph = axes.plot(lambda x: y_func(x)/max_y, x_range=[np.min(x_data), np.max(x_data)], color=axis_color)
            coords = axes.add_coordinates()
            x_label = axes.get_x_axis_label(MathTex(axis_label).next_to(axes.x_axis, RIGHT))
            y_label = axes.get_y_axis_label(MathTex(r"\|\vec{E}(" + axis_label + r")\|").next_to(axes.y_axis, UP))
            return VGroup(axes, graph, x_label, y_label, coords)

        # Sample data for demonstration
        x_data = np.linspace(-X_size/2, X_size/2, 100)
        e_field_x = lambda x: np.abs((1+15*np.exp(-((x - hotspot_location[0])**2 / 0.1 + (hotspot_location[2])**2 / 0.2) ) ) * np.cos(2 * np.pi * np.sqrt((x - hotspot_location[0])**2 + (hotspot_location[2])**2) / 0.3))
        e_field_y = lambda x: np.abs((1+15*np.exp(4)*np.exp(-((hotspot_location[0])**2 / 0.1 + (x - hotspot_location[1])**2 / 0.2) ) ) * np.cos(2 * np.pi * np.sqrt((hotspot_location[0])**2 + (x - hotspot_location[1])**2) / 0.3))
        e_field_z = lambda x: np.abs((1+15*np.exp(4)*np.exp(-((hotspot_location[0])**2 / 0.1 + (x - hotspot_location[1])**2 / 0.3) ) ) * np.cos(2 * np.pi * np.sqrt((hotspot_location[0])**2 + (x - hotspot_location[1])**2) / 0.25))
        #e_field_z = lambda x: np.abs((1+0*np.exp(-((x - hotspot_location[0])**2 / 0.1 + (x - hotspot_location[1])**2 / 0.2) ) ) * np.cos(2 * np.pi * np.sqrt((x - hotspot_location[0])**2) / 0.3))

        # Create graphs
        x_axis_graph = create_graph("x", RED, x_data, e_field_x)
        y_axis_graph = create_graph("y", GREEN, x_data, e_field_y)
        z_axis_graph = create_graph("z", BLUE, x_data, e_field_z)

        # scale the graphs to fit the scene
        x_axis_graph.scale(0.35)
        y_axis_graph.scale(0.35)
        z_axis_graph.scale(0.35)

        # Position the graphs
        x_axis_graph.shift(3 * RIGHT + 2.5 * UP)
        y_axis_graph.shift(3 * RIGHT)
        z_axis_graph.shift(3 * RIGHT + 2.5 * DOWN)

        # Add the graphs to the scene
        self.play(FadeIn(x_axis_graph), run_time=1)
        self.wait(0.5)
        self.next_slide()

        self.play(FadeIn(y_axis_graph), run_time=1)
        self.wait(0.5)
        self.next_slide()

        self.play(FadeIn(z_axis_graph), run_time=1)
        self.wait(0.5)
        self.next_slide()