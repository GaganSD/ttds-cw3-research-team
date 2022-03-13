import React, { Component } from 'react';
import Button from '@mui/material/Button';

export default function QueryExpansionButton(props){
    return(
        <Button variant="contained" color="success" onClick = {() => {
            console.log("hello qe")
            props.parentCallback();

        }
        
        }>
            Suggestion
        </Button>

    );
}