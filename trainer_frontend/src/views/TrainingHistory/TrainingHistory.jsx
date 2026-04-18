import React from 'react';
import { Box, Button, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from "@mui/material";
import "./TrainingHistory.css";
import { Link } from "react-router-dom"; // Assumes you use react-router for navigation

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
};

// Mock data for display - in a real app, this would come from an API
const historicalSessions = [
    { id: 1, date: "2024-05-15", exercise: "Przysiady", duration: 512, reps: 12, status: "🟢 Osiągnięty" },
    { id: 2, date: "2024-05-14", exercise: "Pompki", duration: 77, reps: 15, status: "🟢 Osiągnięty" },
    { id: 3, date: "2024-05-13", exercise: "Pompki", duration: 53, reps: 18, status: "🟢 Osiągnięty" },
    { id: 4, date: "2024-05-12", exercise: "Przysiady", duration: 512, reps: 12, status: "🟢 Osiągnięty" },
    { id: 5, date: "2024-05-11", exercise: "Przysiady", duration: 79, reps: 12, status: "🟢 Osiągnięty" },
];

export default function TrainingHistory() {
    return (
        <Box className="training-history-container">
            {/* Title styled with established slate color and 700 weight */}
            <Typography variant="h1" className="history-title">
                Historia treningu
            </Typography>

            {/* Main historical data view - structured table/list matching the .menuCard established shadow/layout */}
            <TableContainer component={Paper} className="history-card">
                <Table sx={{ minWidth: 650 }} aria-label="history table">
                    <TableHead>
                        <TableRow>
                            {/* Headers use deep slate color, slightly different weight to contrast data */}
                            <TableCell className="table-header">Data</TableCell>
                            <TableCell className="table-header">Ćwiczenie</TableCell>
                            <TableCell className="table-header" align="center">Czas trwania</TableCell>
                            <TableCell className="table-header" align="center">Ilość powtórzeń</TableCell>
                            <TableCell className="table-header" align="right">Cel</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {historicalSessions.map((session) => (
                            <TableRow
                                key={session.id}
                                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                            >
                                <TableCell className="table-data">{session.date}</TableCell>
                                <TableCell className="table-data">{session.exercise}</TableCell>
                                <TableCell className="table-data" align="center">
                                    {formatTime(session.duration)}
                                </TableCell>
                                <TableCell className="table-data" align="center">
                                    {session.reps}
                                </TableCell>
                                <TableCell className="table-data" align="right">
                                    {session.status}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>

                {/* Back button designed exactly like the primary action .homeButton */}
                <Box className="action-button-container">
                    <Button
                        variant="contained"
                        className="backHomeButton"
                        component={Link}
                        to="/" // Navigate to your home route
                    >
                        Back to Home
                    </Button>
                </Box>
            </TableContainer>
        </Box>
    );
}