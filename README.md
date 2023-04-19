# Lineage

Short set of scripts intended to support raid / guild leads in populating DKP
tracking website.

## Instructions

* Install Python 3.10
* Run `pip install -r requirements.txt` to get dependencies.
* Run `python scripts/login.py`
  * Store your auth state in `cookies.pkl`.
* Run `python scripts/get_events.py`
  * Retrieve list of event types using auth state.

## TODO

* Login and store auth state
* Retrieve list of events
* Pick event of interest and add any special metadata
* Read out attendees and format list for upload
