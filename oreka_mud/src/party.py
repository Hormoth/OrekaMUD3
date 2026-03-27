"""
Party / Group system for OrekaMUD3.

Parties are session-only — they are not persisted across reconnects.
"""


class Party:
    def __init__(self, leader):
        self.leader = leader
        self.members = [leader]  # Leader is always first member
        self.pending_invites = []  # List of player names invited

    def invite(self, player_name):
        if player_name not in self.pending_invites:
            self.pending_invites.append(player_name)

    def add_member(self, player):
        if player not in self.members:
            self.members.append(player)
        if player.name in self.pending_invites:
            self.pending_invites.remove(player.name)

    def remove_member(self, player):
        if player in self.members:
            self.members.remove(player)
        if player == self.leader and self.members:
            self.leader = self.members[0]

    def disband(self):
        for member in self.members:
            member.party = None
        self.members.clear()

    def is_member(self, player):
        return player in self.members

    def get_members_in_room(self, room):
        return [m for m in self.members if m.room == room]

    def split_xp(self, total_xp, room):
        """Split XP among party members present in the same room."""
        present = self.get_members_in_room(room)
        if not present:
            return {}
        share = total_xp // len(present)
        result = {}
        for member in present:
            member.xp += share
            result[member.name] = share
        return result

    def get_status(self):
        lines = [f"Party Leader: {self.leader.name}"]
        lines.append("Members:")
        for m in self.members:
            hp_pct = int((m.hp / m.max_hp) * 100) if m.max_hp > 0 else 0
            lines.append(
                f"  {m.name} - Level {m.level} {m.char_class}"
                f" - HP: {m.hp}/{m.max_hp} ({hp_pct}%)"
            )
        if self.pending_invites:
            lines.append(f"Pending invites: {', '.join(self.pending_invites)}")
        return "\n".join(lines)
