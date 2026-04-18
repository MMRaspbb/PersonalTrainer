import { Box, Button, Typography } from "@mui/material";
import "./ChooseExercise.css";
import {useNavigate} from "react-router-dom";

export default function ChooseExercise() {
    const navigate = useNavigate();

    return (
        <Box className="choose-exercises">
            <Box className="menuCard">
                <Typography className="title" >
                    Wybierz ćwiczenie
                </Typography>

                <Button variant="contained" className="homeButton" onClick={() => navigate("/train/squat")}>
                    Przysiady
                </Button>

                <Button variant="contained" className="homeButton" onClick={() => navigate("/train/pushup")}>
                    Pompki
                </Button>
            </Box>
        </Box>
    );
}