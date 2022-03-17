import React, { Component } from 'react';
import Button from '@mui/material/Button';

export default function SearchButton(props){
    return(
        <Button variant="contained" style={{display: 'flex', justifyContent: 'center'}} onClick = {() => {
            props.parentCallback();
        }

        }>
            Search Query
        </Button>

    );
}