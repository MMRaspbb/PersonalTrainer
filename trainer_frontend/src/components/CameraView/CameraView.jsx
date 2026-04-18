import { useEffect, useRef } from "react";

// Add onDataReceived to the props list
export default function CameraView({exercise, timestamp, inProgress, onDataReceived}) {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const socketRef = useRef(null);

    const timestampRef = useRef(timestamp);
    const exerciseRef = useRef(exercise);

    useEffect(() => {
        timestampRef.current = timestamp;
        exerciseRef.current = exercise;
    }, [timestamp, exercise]);

    // WebSocket setup
    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws");
        socket.binaryType = "arraybuffer";

        socket.onopen = () => console.log("WS connected");

        // 🚀 Add the message listener here
        socket.onmessage = (event) => {
            try {
                // Parse the incoming JSON string from the backend
                const data = JSON.parse(event.data);

                // Pass it up to TrainWithPartner if the function was provided
                if (onDataReceived) {
                    onDataReceived(data);
                }
            } catch (err) {
                console.error("Failed to parse incoming WebSocket message:", err);
            }
        };

        socket.onclose = () => console.log("WS closed");
        socket.onerror = (err) => console.error("WS error", err);

        socketRef.current = socket;

        return () => socket.close();
    }, [onDataReceived]);

    // 📷 Camera setup
    useEffect(() => {
        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 640, height: 480 },
                    audio: false,
                });

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (err) {
                console.error("Camera access denied or unavailable", err);
            }
        }

        startCamera();
    }, []);

    // 🚀 Corrected Data Sending Logic
    useEffect(() => {
        // If training is not in progress, don't even start the interval.
        // This is much better for performance than running an empty interval.
        if (!inProgress) return;

        const interval = setInterval(() => {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            const socket = socketRef.current;

            if (!video || !canvas || !socket) return;
            if (socket.readyState !== 1) return; // 1 means OPEN
            if (video.videoWidth === 0) return;

            const ctx = canvas.getContext("2d");

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob((blob) => {
                if (!blob) return;

                const reader = new FileReader();

                reader.onloadend = () => {
                    const payload = {
                        frame: reader.result,
                        // Use the refs here to avoid stale closures without
                        // having to restart the interval every second!
                        timestamp: timestampRef.current,
                        exercise: exerciseRef.current
                    };

                    socket.send(JSON.stringify(payload));
                    console.log(payload)
                };

                reader.readAsDataURL(blob);

            }, "image/jpeg", 0.7);

        }, 100);

        return () => clearInterval(interval);

    }, [inProgress]);

    return (
        <div style={{ width: "100%", maxWidth: "1000px" }}>
            <video
                ref={videoRef}
                autoPlay
                playsInline
                style={{ width: "100%", height: "auto" }}
            />
            <canvas ref={canvasRef} style={{ display: "none" }} />
        </div>
    );
}