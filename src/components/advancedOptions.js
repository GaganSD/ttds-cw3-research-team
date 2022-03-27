import * as React from 'react';
import Box from '@mui/material/Box';
import SwipeableDrawer from '@mui/material/SwipeableDrawer';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox'
import TextField from '@mui/material/TextField';
import AdapterDateFns from '@mui/lab/AdapterDateFns';
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import Stack from '@mui/material/Stack';
import DesktopDatePicker from '@mui/lab/DesktopDatePicker';
import { SliderValueLabelUnstyled } from '@mui/base';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import HelpDialog from "./helpdialog";

import { useEffect, useState } from "react";
import { GlobalStyles } from './global';


import 'typeface-roboto';
import { createTheme, ThemeProvider, styled } from '@mui/material/styles';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

export default function SwipeableTemporaryDrawer(props) {

  const [state, setState] = React.useState({
    top: false,
    left: false,
    bottom: false,
    right: false,
  });

  // let valcopy = {
  //   sort_by: "Featured",
  //   authors: true,
  //   author_text:'',
  //   range_from:null,                                                                                     
  //   range_to: null
  // };

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


  const [fromDate, setFromDate] = React.useState(null);
  const [toDate, setToDate] = React.useState(null);
  const [radio_choice_algorithm, setRadioChoiceAlgorithm] = React.useState("APPROX_NN");
  const [radio_choice_searchtype, setRadioChoiceSearchType] = React.useState("DEFAULT"); 


  React.useEffect(() => {
    console.log(fromDate);
    props.parentCallback("date_from", fromDate);
  }, [fromDate]);


  React.useEffect(() => {
    console.log(toDate);
    props.parentCallback("date_to", toDate);
  }, [toDate]);



  React.useEffect(() => {
    console.log(radio_choice_algorithm);
    props.parentCallback("algorithms", radio_choice_algorithm);
  }, [radio_choice_algorithm]);

  React.useEffect(() => {
    console.log(radio_choice_searchtype)
    props.parentCallback("searchtype", radio_choice_searchtype)
  }, [radio_choice_searchtype]);

  const handleChange = (e) => {
    let eventtype;
    try{
      eventtype = e.target.type;
    }
    catch{
      eventtype = "date";
    }
    if(eventtype === "radio"){
      console.log(props.datasets);
      if(e.target.name === "algorithmbuttons"){
        setRadioChoiceAlgorithm(e.target.value);
      }
      else{
        setRadioChoiceSearchType(e.target.value);
      }
      // setRadioChoiceAlgorithm(e.target.value);
    }


    
    // console.log(radio_choice_algorithm);
    // console.log(toDate);
  };

  const toggleDrawer = (anchor, open) => (event) => {
    if (
      event &&
      event.type === 'keydown' &&
      (event.key === 'Tab' || event.key === 'Shift')
    ) {
      return;
    }

    setState({ ...state, [anchor]: open });
  };
  // const toggleTheme = () => {
  //   console.log("switch");
  //   if (theme === 'light') {
  //     setTheme('dark');
  //   } else {
  //     setTheme('light');
  //   }
  // }
  const list = (anchor) => (
    <Box
      sx={{ width: anchor === 'top' || anchor === 'bottom' ? 'auto' : 400}}
      role="presentation"
      // onClick={toggleDrawer(anchor, false)}
      // onKeyDown={toggleDrawer(anchor, false)}
    >
      <div style = {{
        display : "flex",
        justifyContent: "center"
      }}>
        <h2><b> Advanced Options</b></h2>
        <div style ={{
          marginTop : "1em",
          marginLeft : "1em"
        }}>
          <HelpDialog/>
        </div>
      </div>
      <Divider />

      <List>


        <FormControl sx = {{
          margin:2
        }}>
            <FormLabel id="sortby">Retrieval Algorithm:</FormLabel>
            <RadioGroup
              aria-labelledby='algorithmbuttons'
              defaultValue= {radio_choice_algorithm}
              name = "algorithmbuttons"
              onChange={handleChange}>

                <FormControlLabel control={<Radio/>}  label="Transformers & Nearest Neighbors" value="APPROX_NN" />
                <FormControlLabel control={<Radio/>} label="BM25" value="BM25"/>
                <FormControlLabel control={<Radio/>}  label="TF-IDF" value="TF_IDF"/>

              </RadioGroup>
        </FormControl>

      </List>

      <Divider/>

      <List>
        <FormControl sx = {{
          margin:2
        }}>
            <FormLabel id="sortby">Search Type:</FormLabel>
            <RadioGroup
              aria-labelledby='searchtype options'
              defaultValue= {radio_choice_searchtype}
              name = "searchtypebuttons"
              onChange={handleChange}>

                <FormControlLabel control={<Radio/>}  label="Default" value="DEFAULT" />
                <FormControlLabel control={<Radio/>} label="Proximity Search" value="PROXIMITY"/>
                <FormControlLabel control={<Radio/>}  label="Phrase Search" value="PHRASE"/>
                <FormControlLabel control={<Radio/>} label="Author Search (By Last Name)" value="AUTHOR" disabled={props.datasets}/>
              

              </RadioGroup>
        </FormControl>
      </List>


      <Divider />
      <List>
        <div style = {{
          display : "flex",
          flexDirection: "row"
        }}>
          <CalendarMonthIcon sx={{
            marginTop:".5em",
            marginRight: ".5em",
            marginLeft:".5em"
          }}
          style = {{
            color: 'grey'
          }}
          />
          <p style ={{
            color: "grey"
          }}> Date Range:</p>
        </div>
        <div style={{

        marginRight: "5em",
        marginLeft: "1em"
      
        }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <Stack spacing={3}>
                <DesktopDatePicker
                label="From"
                inputFormat="dd/MM/yyyy"
                value={fromDate}
                onChange={(newfromvalue) => {
                  setFromDate(newfromvalue);
                  handleChange();
                  // console.log(fromDate);
                }}
                renderInput={(params) => <TextField {...params} />}
                />
                <DesktopDatePicker
                label="To"
                inputFormat="dd/MM/yyyy"
                value={toDate}
                onChange={(newtovalue) => {
                  setToDate(newtovalue);
                  handleChange();
                  // console.log(toDate);
                }}
                renderInput={(params) => <TextField {...params} />}
                /> 
              </Stack>
            </LocalizationProvider>
        </div>
      </List>


      <Divider />

{/* 
      <List>
        {['Sort By:', 'Trash', 'Spam'].map((text, index) => (
          <ListItem button key={text}>
            <ListItemIcon>
              {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
            </ListItemIcon>
            <ListItemText primary={text} />
          </ListItem>
        ))}
      </List> */}
    </Box>
  );

  return (

    <div>
        <ThemeProvider theme={theme}>

      {['Advanced Options'].map((anchor) => (
        <React.Fragment key={"left"}>
          <Button onClick={toggleDrawer("left", true)}>{anchor}</Button>
          <SwipeableDrawer
            anchor={"left"}
            open={state["left"]}
            onClose={toggleDrawer("left", false)}
            onOpen={toggleDrawer("left", true)}
          >
            {list("left")}
          </SwipeableDrawer>
        </React.Fragment>
      ))}

    </ThemeProvider>
    </div>
  );
}
