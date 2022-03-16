import React, { Component } from 'react';
import Button from '@mui/material/Button';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import Slide from '@mui/material/Slide';

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});
export default function HelpDialog(props){
    const [open, setOpen] = React.useState(false);
    const handleClickOpen = () => {
        console.log("open")
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };
    return(
        <div>
            <Button variant="contained" onClick={handleClickOpen}>
                ?
            </Button>

            <Dialog
                open={open}
                TransitionComponent={Transition}
                keepMounted
                onClose={handleClose}
                aria-describedby="alert-dialog-slide-description"
                >
                <DialogTitle>{"Get Help with Re-Search?"}</DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-slide-description">
                  This search engine allows you to search for research papers as well as datasets. Simply type in your query in the box above and hit "Search Query" afterwards.
                    Use "Show Suggestions" for spelling correction and make use of the advanced search features (search type, date range, ranking algorithm) to get more refined results! If you want to use dark mode, 
                  simply toggle the switch above the search bar .
                    </DialogContentText>
                </DialogContent>

            </Dialog>
        </div>
    )
}
