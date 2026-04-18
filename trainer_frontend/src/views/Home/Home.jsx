import { Box, Button, Typography } from "@mui/material";
import "./Home.css";
import {useNavigate} from "react-router-dom";

export default function Home() {
    const navigate = useNavigate();

    return (
        <Box className="home">
            <Box className="menuCard">
                <Typography className="title" >
                    Twój Personalny Trener
                </Typography>

                <Button variant="contained" className="homeButton" onClick={() => navigate("/choose/exercise")}>
                    Rozpocznij Ćwiczenia
                </Button>

                <Button variant="contained" className="homeButton">
                    Historia Ćwiczeń
                </Button>

                <Button variant="contained" className="homeButton">
                    Ustawienia
                </Button>
            </Box>
        </Box>
    );
}