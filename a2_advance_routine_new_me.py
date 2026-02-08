class MELevelTables:
    def __init__(self):
        self.tables = {}

    def add_table(self, level, data):
        self.tables[level] = data

    def get_table(self, level):
        return self.tables.get(level, None)

    def reset_level(self, level):
        if level in self.tables:
            del self.tables[level]


class BeelineAdvanceRoutine:
    def __init__(self):
        self.me_level_tables = MELevelTables()

    def manage_merchant_info(self, merchant_id, details):
        # Logic to manage merchant information
        pass

    def reset_me_level(self, level):
        self.me_level_tables.reset_level(level)


# Test Cases

def test_me_level_reset():
    me_level_tables = MELevelTables()
    me_level_tables.add_table(1, {'data': 'value1'})
    me_level_tables.reset_level(1)
    assert me_level_tables.get_table(1) is None, "Level 1 should be reset!"


def test_merchant_info_management():
    advance_routine = BeelineAdvanceRoutine()
    advance_routine.manage_merchant_info('merchant1', {'name': 'Merchant A', 'status': 'active'})
    # Add assertions to verify the merchant information is managed correctly


# Running test cases
if __name__ == '__main__':
    test_me_level_reset()
    test_merchant_info_management()