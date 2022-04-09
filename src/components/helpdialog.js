import React from 'react';
import Button from '@mui/material/Button';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import Slide from '@mui/material/Slide';

import 'typeface-roboto';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});
export default function HelpDialog(props){


    const [open, setOpen] = React.useState(false);
    const handleClickOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };
    const theme = createTheme({
        components: {
          MuiTypography: {
            defaultProps: {
              variantMapping: {
                h1: 'h2',
                h2: 'h2',
                h3: 'h2',
                h4: 'h2',
                h5: 'h2',
                h6: 'h2',
                subtitle1: 'h2',
                subtitle2: 'h2',
                body1: 'span',
                body2: 'span',
              },
            },
          },
        },
      });
    return(

        <div>
        <ThemeProvider theme={theme}>


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
                        You can use the advanced search options to refine your search. 
                        
                        We provide three different ranking algorithms: <a href="https://ieeexplore.ieee.org/document/6809191">SCANN</a>,
                         <a href="https://aclanthology.org/W16-2365.pdf"> Cosine TF-IDF</a>, and <a href="https://en.wikipedia.org/wiki/Okapi_BM25">BM25</a>
                        <br/><br/>
                        For research papers, you can also choose between Proximity, Phrase, and Author search types. For datasets, we provide the same 
                        options with an exception of Author Search since this field is missing in many open-source datasets.

                        Other than this, you can filter your results with 'from' and 'to' dates in both datasets and papers or use the "Expand Query" option to get
                        synonyms through WordNet.

                        <br/>
                        <br/>
                        NOTE: Please note that the same author's name might vary in the paper.
                        For example, some papers list John A. Zoidberg's name as "J. Zoidberg" while others
                        can list them as "J. Zoidberg" or even just "Zoidberg". We recommend searching by lastname to deal with this.
                    </DialogContentText>
                </DialogContent>

            </Dialog>
        </ThemeProvider>

        </div>
    )
}
