import React from 'react';
import Button from '@mui/material/Button';

export default function SearchButton(props){
    console.log("rerenderinnggg");

    const handleClick = () =>{
        console.log(props.link)
    }

    if (props.homepage === true){
        return(
            <Button title="Search Query With Given Configurations" variant="contained" style={{display: 'flex', justifyContent:'center'}} onClick={handleClick}>
                Search
            </Button>
        )
    }
    return(
        <Button title="Search Query With Given Configurations" variant="contained" style={{display: 'flex', justifyContent: 'center'}} onClick = { async () => {
        }
        }>
            Search
        </Button>

    );
}