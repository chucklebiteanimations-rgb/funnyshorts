import ffmpeg
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def create_video_from_image(image_path, output_path, duration=60):
    """
    Creates a 60-second vertical video from an image with a slow zoom effect.
    """
    try:
        # Input image
        input_stream = ffmpeg.input(image_path, loop=1, t=duration)

        # Zoom effect (ken burns) + ensure vertical 9:16 aspect ratio (1080x1920)
        # We start with zoom 1 and go to zoom 1.1 over duration
        # We crop to 9:16
        
        # Simple zoom pan
        # 'zoompan=z=\'min(zoom+0.0015,1.5)\':d=60*25:s=1080x1920'
        # Note: scale=-1:1920 sets height to 1920 and width proportionally, then crop
        
        # To strictly force 1080x1920 from any source:
        # 1. Scale to cover 1080x1920 (preserving aspect ratio)
        # 2. Crop center 1080x1920
        # 3. Apply Zoom
        
        # Let's try a simpler approach compatible with most ffmpeg builds:
        # Scale to height 1920, then crop width to 1080
        
        processed = (
            input_stream
            .filter('scale', w=-1, h=1920)
            .filter('crop', w=1080, h=1920)
             # Zoom in slowly to 1.1x over the duration
            .filter('zoompan', z='min(zoom+0.0005,1.2)', d=duration*30, s='1080x1920', fps=30)
        )

        output = (
            processed
            .output(output_path, t=duration, vcodec='libx264', pix_fmt='yuv420p', r=30)
            .overwrite_output()
        )
        
        output.run(capture_stdout=True, capture_stderr=True)
        print(f"Video created: {output_path}")
        return True

    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode('utf8')}")
        return False
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return False

def add_watermark(video_path, watermark_path, output_path):
    """
    Overlays a TEXT watermark on the video (Top Left).
    Ignores watermark_path (kept for compatibility) and uses fixed text.
    """
    try:
        main = ffmpeg.input(video_path)
        
        # Drawtext filter
        # text='ChuckleBites'
        # x=10 (padding from left)
        # y=10 (padding from top)
        # fontsize=50 (visible on 1080p)
        # fontcolor=white
        # shadowcolor=black (for visibility)
        # shadowx=2, shadowy=2
        # fontfile: Try Arial. If it fails, ffmpeg often has a default or needs a path.
        # On Windows: C:/Windows/Fonts/arial.ttf
        
        processed = main.filter(
            'drawtext',
            text='ChuckleBites',
            x=20,
            y=20,
            fontsize=60,
            fontcolor='white',
            shadowcolor='black@0.5',
            shadowx=3,
            shadowy=3,
            fontfile='C:/Windows/Fonts/arial.ttf' 
        )
        
        audio = main.audio
        
        output = (
            ffmpeg.output(processed, audio, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', r=30)
            .overwrite_output()
        )
        
        output.run(capture_stdout=True, capture_stderr=True)
        print(f"Text watermarked video created: {output_path}")
        return True
        
    except ffmpeg.Error as e:
        print(f"FFmpeg watermark error: {e.stderr.decode('utf8')}")
        return False
    except Exception as e:
        print(f"Error adding watermark: {str(e)}")
        return False

if __name__ == "__main__":
    # Test block
    test_img = os.path.join(config.SHORTS_DIR, "Day_1", "image.jpg") # Assuming typical structure
    # If Day_1 exists, we can try to find a file there
    
    # We will search for a test file dynamically
    day_1_path = os.path.join(config.SHORTS_DIR, "Day_1")
    test_file = None
    if os.path.exists(day_1_path):
        for f in os.listdir(day_1_path):
            if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                test_file = os.path.join(day_1_path, f)
                break
    
    if test_file:
         print(f"Testing with {test_file}")
         temp_video = "test_video.mp4"
         create_video_from_image(test_file, temp_video, duration=5)
         
         # Check for watermark
         # We need a dummy watermark if one doesn't exist
         # watermark_file = os.path.join(config.ASSETS_DIR, "watermark.png")
         # if os.path.exists(watermark_file):
         #    add_watermark(temp_video, watermark_file, "test_final.mp4")
    else:
        print("No test image found in Day_1")
