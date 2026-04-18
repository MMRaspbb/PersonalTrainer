import CameraView from "../../components/CameraView/CameraView.jsx";
import {Box, Button} from "@mui/material";
import "./TrainWithPartner.css";
import {useEffect, useId, useState} from "react";
import {useParams} from "react-router-dom";

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;

    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
};

export default function TrainWithPartner() {

    const exercise = useParams().exercise

    const [timestamp, setTimestamp] = useState(.0)
    const [inProgress, setInProgress] = useState(false)

    const startStop = () => {
        if (!inProgress) {
            setTimestamp(0);
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

    return (
        <Box className="train-with-partner">
            <Box className="camera-container">
                <CameraView exercise={exercise} timestamp={timestamp} inProgress={inProgress}/>

                <Box className="feedback">🟢 Good form</Box>

                <Box className="reps-time">
                    <p>Reps: 8</p>
                    <p>{formatTime(timestamp)}</p>
                </Box>
            </Box>
            <Box>
                <Button variant="outlined" className="startButton" onClick={() => startStop()}>
                    {inProgress ? 'Stop' : 'Start'}
                </Button>
            </Box>
        </Box>
    );
}