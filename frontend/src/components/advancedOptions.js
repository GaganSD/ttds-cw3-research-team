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


export default function SwipeableTemporaryDrawer() {
  const [state, setState] = React.useState({
    top: false,
    left: false,
    bottom: false,
    right: false,
  });

  const [values,setValues] = React.useState({
    oldest: false,
    latest: false,
    featured: true,
    authors: true,
    range: false,
    author_text:'',
    range_from:new Date(),
    range_to: new Date()
  })

  const handleChange = (newValue) => {
    setValues(newValue);
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
      onKeyDown={toggleDrawer(anchor, false)}
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
            <FormControlLabel control={<Checkbox  />} label="Oldest" />
            <FormControlLabel control={<Checkbox  />} label="Latest" />
            <FormControlLabel control={<Checkbox defaultChecked />} label="Featured" />
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

        <TextField id="outlined-basic" label="Authors" variant="outlined"/>

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
              value={values.range_from}
              onChange={handleChange}
              renderInput={(params) => <TextField {...params} />}
            />
            <DesktopDatePicker
              label="To"
              inputFormat="MM/dd/yyyy"
              value={values.range_to}
              onChange={handleChange}
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
