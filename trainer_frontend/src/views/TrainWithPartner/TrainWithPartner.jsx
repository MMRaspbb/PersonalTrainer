import CameraView from "../../components/CameraView/CameraView.jsx";
import {Box, Button} from "@mui/material";
import "./TrainWithPartner.css";
import {useEffect, useState} from "react";
import {useParams} from "react-router-dom";

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;

    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
};

export default function TrainWithPartner() {
    const {exercise} = useParams();

    const [timestamp, setTimestamp] = useState(0);
    const [inProgress, setInProgress] = useState(false);

    // 1. Add state for the dynamic data you want to receive
    const [reps, setReps] = useState(0);
    const [feedback, setFeedback] = useState("🟢 Waiting for data...");

    const startStop = () => {
        if (!inProgress) {
            setTimestamp(0);
            setReps(0); // Optional: reset reps on start
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

    // 2. Create a handler for incoming WebSocket data
    const handleSocketData = (data) => {
        // Backend wysyła 'rep_count', a nie 'reps'!
        if (data.rep_count !== undefined) {
            setReps(data.rep_count);
        }
        if (data.feedback !== undefined) {
            setFeedback(data.feedback);
        }
    };

    return (
        <Box className="train-with-partner">
            <Box className="camera-container">
                <CameraView
                    exercise={exercise}
                    timestamp={timestamp}
                    inProgress={inProgress}
                    onDataReceived={handleSocketData}
                />
                e
                <Box className="feedback">{feedback}</Box>

                <Box className="reps-time">
                    <p>Reps: {reps}</p>
                    <p>{formatTime(timestamp)}</p>
                </Box>
            </Box>
            <Box>
                <Button variant="outlined" className="startButton" onClick={startStop}>
                    {inProgress ? 'Stop' : 'Start'}
                </Button>
            </Box>
        </Box>
    );
}