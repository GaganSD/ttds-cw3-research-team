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
                <DialogTitle>{"Need Help with Re-Search?"}</DialogTitle>
                <DialogContent>
                    <DialogContentText id="alert-dialog-slide-description">
                  The advanced search features can be used to refine your search, if you have specific requirements (ranking algorithm, search type, date range) in addition to your query in mind! 
                  If not, leave the options set to their default values and just type your query in the "Query" box, and hit "Search Query" afterwards.
                  Use "Show Suggestions" for spelling correction suggestions. If you want to use dark mode, simply toggle the switch above the search bar.
                    </DialogContentText>
                </DialogContent>

            </Dialog>
        </div>
    )
}
