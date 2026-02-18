import streamlit as st
import subprocess
import os
import tempfile
import zipfile
from pathlib import Path

st.set_page_config(page_title="Video Downscaler", page_icon="🎬", layout="centered")

st.title("🎬 Video Downscaler")
st.caption("Downscale your videos to 1280×720 (720p)")

uploaded_files = st.file_uploader(
    "Upload your videos",
    type=["mp4", "mov", "avi", "mkv", "webm", "flv"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.write(f"**{len(uploaded_files)} video(s) ready to process**")

    if st.button("⚡ Start Downscaling", use_container_width=True, type="primary"):
        output_paths = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_placeholder = st.container()

        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing: {uploaded_file.name} ({i + 1}/{len(uploaded_files)})")

            suffix = Path(uploaded_file.name).suffix or ".mp4"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
                tmp_in.write(uploaded_file.read())
                input_path = tmp_in.name

            output_filename = f"720p_{Path(uploaded_file.name).stem}.mp4"
            output_path = os.path.join(tempfile.gettempdir(), output_filename)

            try:
                cmd = [
                    "ffmpeg", "-y",
                    "-i", input_path,
                    "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
                    "-vcodec", "libx264",
                    "-acodec", "aac",
                    "-crf", "23",
                    "-preset", "fast",
                    output_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    output_paths.append((output_filename, output_path))
                    with results_placeholder:
                        st.success(f"✅ {uploaded_file.name} → done")
                else:
                    with results_placeholder:
                        st.error(f"❌ Failed: {uploaded_file.name}\n{result.stderr[-300:]}")
            except FileNotFoundError:
                st.error("❌ FFmpeg binary not found. Make sure packages.txt contains 'ffmpeg'.")
                break
            finally:
                if os.path.exists(input_path):
                    os.unlink(input_path)

            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text("All done! Download your files below.")

        if output_paths:
            st.divider()
            st.subheader("📥 Download")

            if len(output_paths) == 1:
                name, path = output_paths[0]
                with open(path, "rb") as f:
                    st.download_button(
                        label=f"Download {name}",
                        data=f,
                        file_name=name,
                        mime="video/mp4",
                        use_container_width=True,
                    )
            else:
                zip_path = os.path.join(tempfile.gettempdir(), "downscaled_videos.zip")
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for name, path in output_paths:
                        zipf.write(path, name)

                with open(zip_path, "rb") as f:
                    st.download_button(
                        label=f"📦 Download All ({len(output_paths)} videos) as ZIP",
                        data=f,
                        file_name="downscaled_videos.zip",
                        mime="application/zip",
                        use_container_width=True,
                    )

                st.divider()
                st.write("**Or download individually:**")
                for name, path in output_paths:
                    with open(path, "rb") as f:
                        st.download_button(
                            label=f"⬇️ {name}",
                            data=f,
                            file_name=name,
                            mime="video/mp4",
                            use_container_width=True,
                        )
