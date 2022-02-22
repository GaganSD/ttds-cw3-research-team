import * as React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';

export default function FilterButton(){
    return(
        <ButtonGroup variant="contained" aria-label="outlined primary button group">
            <Button>Papers</Button>
            <Button>Data Set</Button>
        </ButtonGroup>
    )
}