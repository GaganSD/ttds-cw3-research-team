import React, { Component } from 'react';
import Button from '@mui/material/Button';

export default function HelpButton(props){
    return(
        <Button variant="contained" onClick = {() => {props.parentCallback();}}>?</Button>
        );
}