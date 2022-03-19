import React, { Component } from 'react';
import Button from '@mui/material/Button';
import LoadingButton from '@mui/lab/LoadingButton';

export default function SearchButton(props){

const [process, setProcess] = React.useState({label: 'Search Query'})
async function task() {
    return new Promise(() => {
        props.parentCallback();
      })
  }
    return(
        <Button variant="contained" style={{display: 'flex', justifyContent: 'center'}} onClick = { async () => {
            
            
            setProcess({label: 'Loading...' });
            const promises = await task();
            promises.then(setProcess({label: 'Search Query'}));


           //another attempt that doesnt work:
           //setProcess({label: 'Loading...' }).then(props.parentCallback()).then(setProcess({label: 'Search Query'}));
                
        }
        }>
            {process.label}
        </Button>

    );
}


//this is just the old code in case i/we dont figure out how to make it dependent on the retrieval:
/* import React, { Component } from 'react';
import Button from '@mui/material/Button';
import LoadingButton from '@mui/lab/LoadingButton';

export default function SearchButton(props){

const [process, setProcess] = React.useState({label: 'Search Query'})

    return(
        <Button variant="contained" style={{display: 'flex', justifyContent: 'center'}} onClick = {() => {
            setProcess({label: 'Loading...' });

            //var a = performance.now();
            props.parentCallback();
            //var b = performance.now();
            //var exectime=b-a;

            setTimeout(() => { 
                setProcess({ 
                    label: 'Search Query'
                })}, 500); //this timeout is just here so that the loading does show up... so basically what needs to 
                //go here instead of 500 is the time it takes to execute props.parentCallback I think?? the commented code above doesn't work...but idk how to kinda do it at runtime:(
        }
        }>
            {process.label}
        </Button>

    );
} */