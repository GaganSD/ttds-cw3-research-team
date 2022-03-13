import React, { Component } from 'react';
import Button from '@mui/material/Button';

export default function SearchButton(props){
    return(
        <Button variant="contained" color="success" onClick = {() => {
            console.log("nooo 2.0")
            props.parentCallback();
        }

        }>
            Search
        </Button>

    );
}