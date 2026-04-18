import CameraView from "../../components/CameraView/CameraView.jsx";
import { Box } from "@mui/material";
import "./TrainWithPartner.css";

export default function TrainWithPartner() {
    return (
        <Box className="train-with-partner">
            <Box className="camera-container">
                <CameraView />

                <Box className="feedback">🟢 Good form</Box>

                <Box className="reps-time">
                    <p>Reps: 8</p>
                    <p>00:32</p>
                </Box>
            </Box>
        </Box>
    );
}