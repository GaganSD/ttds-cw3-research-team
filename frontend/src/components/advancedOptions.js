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

export default function SwipeableTemporaryDrawer() {
  const [state, setState] = React.useState({
    top: false,
    left: false,
    bottom: false,
    right: false,
  });

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
      onClick={toggleDrawer(anchor, false)}
      onKeyDown={toggleDrawer(anchor, false)}
    >
      <List>

        <ListItem button key={"Custom Search: "}>
        <ListItemIcon>
        <InboxIcon />
        </ListItemIcon>
        <ListItemText primary={"Custom Search: "} />
        </ListItem>

        <ListItem button key={"Papers"}>
        <ListItemIcon>
        <MailIcon />
        </ListItemIcon>
        <ListItemText primary={"Papers"} />
      </ListItem>

      <ListItem button key={"Datasets"}>
        <ListItemIcon>
        <MailIcon />
        </ListItemIcon>
        <ListItemText primary={"Datasets"} />
      </ListItem>

      </List>

      <Divider />

      <List>

        <ListItem button key={"Sort By: "}>
        <ListItemIcon>
        <InboxIcon />
        </ListItemIcon>
        <ListItemText primary={"Sort By: "} />
        </ListItem>

        <ListItem button key={"Latest"}>
        <ListItemIcon>
        <MailIcon />
        </ListItemIcon>
        <ListItemText primary={"Latest"} />
        </ListItem>

        <ListItem button key={"Oldest"}>
        <ListItemIcon>
        <MailIcon />
        </ListItemIcon>
        <ListItemText primary={"Oldest"} />
      </ListItem>

      <ListItem button key={"Featured"}>
        <ListItemIcon>
        <MailIcon />
        </ListItemIcon>
        <ListItemText primary={"Featured"} />
      </ListItem>

      </List>

      <Divider />

      <List>

        <ListItem button key={"Publication"}>
        <ListItemIcon>
        <InboxIcon />
        </ListItemIcon>
        <ListItemText primary={"Publication"} />
        </ListItem>

        <ListItem button key={"Range:"}>
        <ListItemIcon>
        <MailIcon />
        </ListItemIcon>
        <ListItemText primary={"Range:"} />
        </ListItem>

        <ListItem button key={"From & to"}>
        <ListItemIcon>
        <InboxIcon />
        </ListItemIcon>
        <ListItemText primary={"From & to"} />
      </ListItem>

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
