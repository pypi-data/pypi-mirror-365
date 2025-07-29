import logging
from typing import Optional

from buco_db_controller.models.team import Team


class Odds:
    def __init__(
            self,
            fixture_id: int,
            ht: Team,
            at: Team,
            result: dict,
            over_under: dict,
            btts: dict,
            dnb: dict,
            handicap: dict
    ):
        self.fixture_id: int = fixture_id
        self.ht: Team = ht
        self.at: Team = at
        self.result: dict = result
        self.over_under: dict = over_under
        self.btts: dict = btts
        self.dnb: dict = dnb
        self.handicap: dict = handicap

    @classmethod
    def from_dict(cls, response: dict) -> Optional['Odds']:
        data = response['data']

        #TODO: This is a temporary fix to handle different naming conventions in odds data
        if "1x2" not in data.get('odds', {}):
            logging.error(f"Odds data for fixture {response} does not contain '1x2' odds. (only '1X2' is supported)")
            return None

        return cls(
            fixture_id=response['parameters']['fixture'],
            ht=Team(
                team_id=data['home']['team']['id'],
                name=data['home']['team']['name']
            ),
            at=Team(
                team_id=data['away']['team']['id'],
                name=data['away']['team']['name']
            ),
            result=data['odds']['1x2'],
            over_under=data['odds']['over/under'],
            btts=data['odds']['both teams to score'],
            dnb=data['odds']['draw no bet'],
            handicap=data['odds']['asian handicap']
        )
