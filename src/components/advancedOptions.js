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


export default function SwipeableTemporaryDrawer(props) {
  const [state, setState] = React.useState({
    top: false,
    left: false,
    bottom: false,
    right: false,
  });

  let valcopy = {
    oldest: false,
    latest: false,
    featured: true,
    authors: true,
    author_text:'',
    range_from:null,
    range_to: null
  };

  const [fromDate, setFromDate] = React.useState(null);
  const [toDate, setToDate] = React.useState(null);




  const handleChange = (e) => {
    let eventtype;
    try{
      eventtype = e.target.type;
    }
    catch{
      eventtype = "date";
    }
    // console.log(e.target.checked)
    if(eventtype === "checkbox"){
      if(e.target.value === "Oldest"){
        valcopy.oldest = e.target.checked;
      }
      else if(e.target.value === "Latest"){
        valcopy.latest = e.target.checked;
      }
      else{
        valcopy.featured = e.target.checked;
      }

    }
    else if(eventtype === "text"){
      if(e.target.value !== ''){
        valcopy.authors = true;
        valcopy.author_text = e.target.value
      }

    }
    else if(eventtype === "date"){
      //some logic to make sureincompatible date ranges are not entered
      //not too important can look into it later
      // if (valcopy.range_from >= valcopy.range_to){
      //   alert("from date has to be lesser than the to date!");
      //   valcopy.range_from =null;
      //   setFromDate(null);
      // }

    }



    props.parentCallback(valcopy)
    // console.log(valcopy);
    // setValues(newValue);
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

  const list = (anchor) => (
    <Box
      sx={{ width: anchor === 'top' || anchor === 'bottom' ? 'auto' : 250 }}
      role="presentation"
      // onClick={toggleDrawer(anchor, false)}
      // onKeyDown={toggleDrawer(anchor, false)}
    >

      <Divider />

      <List>

        <ListItem button key={"Sort By: "}>
        <ListItemIcon>
        <InboxIcon />
        </ListItemIcon>
        <ListItemText primary={"Sort By: "} />
        </ListItem>

        <FormGroup>
            <FormControlLabel control={<Checkbox  />} onChange={handleChange} label="Oldest" value="Oldest" />
            <FormControlLabel control={<Checkbox />} onChange={handleChange} label="Latest" value="Latest"/>
            <FormControlLabel control={<Checkbox defaultChecked />} onChange={handleChange} label="Featured" value="Featured"/>
        </FormGroup>




      </List>

      <Divider />

      <List>

        <ListItem button key={"Authors"}>
        <ListItemIcon>
        <InboxIcon />
        </ListItemIcon>
        <ListItemText primary={"Authors"} />
        </ListItem>

        <TextField onChange = {handleChange} id="outlined-basic" label="Authors" variant="outlined"/>

        <ListItem button key={"Range:"}>
        <ListItemIcon>
        <MailIcon />
        </ListItemIcon>
        <ListItemText primary={"Range:"} />
        </ListItem>


        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <Stack spacing={3}>
            <DesktopDatePicker
            label="From"
            inputFormat="MM/dd/yyyy"
            value={fromDate}
            onChange={(newfromvalue) => {
              setFromDate(newfromvalue);
              valcopy.range_from = fromDate;
              handleChange();
              // console.log(fromDate);
            }}
            renderInput={(params) => <TextField {...params} />}
            />
            <DesktopDatePicker
            label="To"
            inputFormat="MM/dd/yyyy"
            value={toDate}
            onChange={(newtovalue) => {
              setToDate(newtovalue);
              valcopy.range_to = toDate;
              handleChange();
              // console.log(toDate);
            }}
            renderInput={(params) => <TextField {...params} />}
            /> 
          </Stack>
        </LocalizationProvider>

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
      {['Advanced Search Options'].map((anchor) => (
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
    </div>
  );
}
