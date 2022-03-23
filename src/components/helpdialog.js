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
                <DialogTitle>{"Advanced Options Help:"}</DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-slide-description">
                  The advanced search features can be used to refine your search and help satisfy specific requirements for your queries.     
                  You can choose between three different ranking algorithms and pick one of the follwing search types: Transformers, Proximity Search, Phrase Search, or Author Search.
                  Furthermore, you can specify a date range for the publication date of the paper(s)/dataset(s) you are searching for. 
                  If you do not have specific requirements in mind, just leave the options set to their default values, type your query in the "Query" box, and hit "Search Query" afterwards.
                    </DialogContentText>
                </DialogContent>

            </Dialog>
        </div>
    )
}
