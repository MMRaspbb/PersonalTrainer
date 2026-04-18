export function captureFrame(video, canvas) {
    if (!video || !canvas) return null;
    if (video.videoWidth === 0) return null;

    const ctx = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL("image/jpeg");
}