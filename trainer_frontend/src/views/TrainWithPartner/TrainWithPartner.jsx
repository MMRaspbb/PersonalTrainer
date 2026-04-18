import CameraView from "../../components/CameraView/CameraView.jsx";
import { Box, Button } from "@mui/material";
import "./TrainWithPartner.css";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;

    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
};

export default function TrainWithPartner() {
    const { exercise } = useParams();

    const [timestamp, setTimestamp] = useState(0);
    const [inProgress, setInProgress] = useState(false);

    const [reps, setReps] = useState(0);
    const [feedback, setFeedback] = useState("Wciśnij start aby rozpocząć");

    const startStop = () => {
        if (!inProgress) {
            setTimestamp(0);
            setReps(0);
        }
        else{
            setFeedback("Wciśnij start aby rozpocząć")
        }
        setInProgress(prev => !prev);
    };

    useEffect(() => {
        let interval = null;

        if (inProgress) {
            const startTime = Date.now();

            interval = setInterval(() => {
                setTimestamp(Math.floor((Date.now() - startTime) / 1000));
            }, 1000);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [inProgress]);

    const handleSocketData = (data) => {
        if (data.reps !== undefined) {
            setReps(data.reps);
        }
        if (data.feedback !== undefined) {
            setFeedback(data.feedback);
        }
    };

    return (
        <Box className="train-with-partner">
            {/* 1. Feedback Box - Conditionally add "error-flash" class */}
            <Box
                className={`feedback-box ${feedback.includes("Nie wykryto postaci") ? "error-flash" : ""}`}
            >
                {feedback}
            </Box>

            {/* 2. Camera Container */}
            <Box className="camera-container">
                <CameraView
                    exercise={exercise}
                    timestamp={timestamp}
                    inProgress={inProgress}
                    onDataReceived={handleSocketData}
                />

                {/* Score & Time */}
                <Box className="reps-time">
                    <p style={{ margin: 0 }}>Score: {reps}</p>
                    <p style={{ margin: 0 }}>{formatTime(timestamp)}</p>
                </Box>

                {/* Goal */}
                <Box className="goal-box">
                    <p style={{ margin: 0 }}>Goal: 10</p>
                </Box>
            </Box>

            {/* 3. Button Container */}
            <Box>
                <Button variant="outlined" className="startButton" onClick={startStop}>
                    {inProgress ? 'Stop' : 'Start'}
                </Button>
            </Box>
        </Box>
    );
}