import { useEffect, useRef } from "react";

export default function CameraView() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const socketRef = useRef(null);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws");
        socket.binaryType = "arraybuffer";

        socket.onopen = () => {
            console.log("WS connected");
        };

        socket.onclose = () => {
            console.log("WS closed");
        };

        socket.onerror = (err) => {
            console.error("WS error", err);
        };

        socketRef.current = socket;

        return () => socket.close();
    }, []);

    // 📷 Kamera
    useEffect(() => {
        async function startCamera() {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: false,
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
        }

        startCamera();
    }, []);

    // 🎥 Capture + send
    useEffect(() => {
        const interval = setInterval(() => {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            const socket = socketRef.current;

            if (!video || !canvas || !socket) return;
            if (socket.readyState !== 1) return;
            if (video.videoWidth === 0) return;

            const ctx = canvas.getContext("2d");

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            // 🔥 TU KLUCZ: Blob zamiast base64
            canvas.toBlob(
                (blob) => {
                    if (blob) {
                        socket.send(blob);
                    }
                },
                "image/jpeg",
                0.7 // jakość (0–1)
            );
        }, 100); // ~10 FPS

        return () => clearInterval(interval);
    }, []);

    return (
        <div>
            <video
                ref={videoRef}
                autoPlay
                playsInline
                style={{ width: "640px" }}
            />

            <canvas ref={canvasRef} style={{ display: "none" }} />
        </div>
    );
}