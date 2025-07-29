from typing import Optional


class FixtureStats:
    def __init__(
            self,
            fixture_id: int,
            home: Optional[dict],
            away: Optional[dict]
    ):
        self.fixture_id: int = fixture_id
        self.home: dict = home
        self.away: dict = away

    @classmethod
    def from_dict(cls, response: dict) -> 'FixtureStats':
        fixture_id = response['parameters']['fixture']
        data = response.get('data') or {}
        return cls(
            fixture_id=fixture_id,
            home=data.get('home'),
            away=data.get('away')
        )
