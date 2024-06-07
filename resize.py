import io
from PIL import Image, ImageSequence

def resize_frame(frame, target_width, target_height, background_color):
    # Calculate the new size preserving the aspect aspect_ratio
    original_width, original_height = frame.size
    ratio = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    # Resize the frame
    frame = frame.resize((new_width, new_height), Image.LANCZOS)

    # Create a new image with specified background color and target size
    new_frame = Image.new('RGB', (target_width, target_height), background_color)

    # Calculate the positioning for the new frame to be centered
    top_left_x = (target_width - new_width) // 2
    top_left_y = (target_height - new_height) // 2

    # Paste the resized frame onto the new frame
    new_frame.paste(frame, (top_left_x, top_left_y))
    return new_frame

def optimize_and_save_gif(frames, output_path, initial_duration, max_size=1_000_000):
    # Attempt to save with reduced frame rates and color palettes
    for colors in [256, 128, 64, 32]:  # Reduce the number of colors
        for skip in range(1, 3):  # Increase frame skipping
            duration = initial_duration * skip
            optimized_frames = [frame.convert('P', palette=Image.ADAPTIVE, colors=colors) for frame in frames[::skip]]
            buffer = io.BytesIO()
            optimized_frames[0].save(buffer, format='GIF', save_all=True, append_images=optimized_frames[1:], loop=0, duration=duration, optimize=True)
            if buffer.tell() <= max_size:
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())
                return True
    return False

def resize_and_optimize_gif(input_path, output_path, target_width=160, target_height=128, background_color=(0, 0, 0)):
    img = Image.open(input_path)
    frames = []

    # Prepare each frame
    for frame in ImageSequence.Iterator(img):
        frame = frame.convert('RGBA')
        frame = Image.alpha_composite(Image.new('RGBA', frame.size, background_color), frame).convert('RGB')
        resized_frame = resize_frame(frame, target_width, target_height, background_color)
        frames.append(resized_frame)

    # Try to optimize and save the GIF
    if not optimize_and_save_gif(frames, output_path, img.info.get('duration', 100)):
        print("Could not reduce GIF size under 1MB with current settings.")

# Example usage
input_gif_path = './input.gif'
output_gif_path = './output.gif'
resize_and_optimize_gif(input_gif_path, output_gif_path)
