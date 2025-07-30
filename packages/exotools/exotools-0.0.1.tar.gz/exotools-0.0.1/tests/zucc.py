from exotools import KnownExoplanetsDataset
from exotools.io import FeatherStorage
from tests.conftest import TEST_TMP_DIR


def main():
    storage = FeatherStorage(root_path=TEST_TMP_DIR)
    exo_db = KnownExoplanetsDataset(storage=storage).download_known_exoplanets(limit=10, with_gaia_star_data=True)
    print(exo_db.ids)


if __name__ == "__main__":
    main()
