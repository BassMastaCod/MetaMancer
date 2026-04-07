from pathlib import Path

import pytest

from metamancer import SpatialStrata


@pytest.fixture
def location_taxonomy():
    taxonomy = SpatialStrata()
    taxonomy.add_files(
        Path('roadtrip 01.jpg'),
        Path('roadtrip 02.jpg'),
        Path('roadtrip 03.jpg')
    )

    vacation = SpatialStrata('Vacation')
    vacation.add_files(
        Path('vacation 01.jpg'),
        Path('vacation 02.jpg'),
        Path('vacation 03.jpg')
    )
    taxonomy.nest_stratum(vacation)

    town = SpatialStrata('Town')
    town.add_files(
        Path('store.jpg'),
        Path('work.jpg'),
        Path('relatives.jpg')
    )
    taxonomy.nest_stratum(town)

    neighborhood = SpatialStrata('Neighborhood')
    neighborhood.add_files(
        Path('neighbor.jpg'),
        Path('pond.jpg'),
        Path('park.jpg')
    )
    town.nest_stratum(neighborhood)

    neighbor = SpatialStrata('Neighbor')
    neighbor.add_files(
        Path('neighbor house 01.jpg'),
        Path('neighbor house 02.jpg'),
        Path('neighbor garden.jpg')
    )
    neighborhood.nest_stratum(neighbor)

    home = SpatialStrata('Home')
    home.add_files(
        Path('house 01.jpg'),
        Path('house 02.jpg'),
        Path('house 03.jpg'),
        Path('house 04.jpg'),
        Path('house 05.jpg'),
        Path('house 06.jpg')
    )
    neighborhood.nest_stratum(home)

    yard = SpatialStrata('Yard')
    yard.add_files(
        Path('backyard 01.jpg'),
        Path('backyard 02.jpg'),
        Path('frontyard.jpg'),
        Path('driveway.jpg'),
        Path('pool.jpg'),
        Path('shed.jpg')
    )
    home.nest_stratum(yard)

    return taxonomy


def assert_files(actual: list, *expected: str) -> None:
    assert set(actual) == {Path(file) for file in expected}


def test_files(location_taxonomy):
    assert_files(location_taxonomy.files,
        'vacation 01.jpg',
        'vacation 02.jpg',
        'vacation 03.jpg',

        'store.jpg',
        'work.jpg',
        'relatives.jpg',

        'neighbor.jpg',
        'pond.jpg',
        'park.jpg',

        'neighbor house 01.jpg',
        'neighbor house 02.jpg',
        'neighbor garden.jpg',

        'house 01.jpg',
        'house 02.jpg',
        'house 03.jpg',
        'house 04.jpg',
        'house 05.jpg',
        'house 06.jpg',

        'backyard 01.jpg',
        'backyard 02.jpg',
        'frontyard.jpg',
        'driveway.jpg',
        'pool.jpg',
        'shed.jpg',

        'roadtrip 01.jpg',
        'roadtrip 02.jpg',
        'roadtrip 03.jpg'
    )


def test_files__empty():
    assert_files(SpatialStrata().files)


def test_files__empty__nested():
    nested = SpatialStrata()
    sub = SpatialStrata()
    nested._nested_files['Sub'] = sub
    assert_files(SpatialStrata().files)


def test_files__only_direct(location_taxonomy):
    vacation = location_taxonomy._nested_files['Vacation']
    assert not vacation._nested_files
    assert_files(vacation.files,
        'vacation 01.jpg',
        'vacation 02.jpg',
        'vacation 03.jpg'
    )


def test_files__only_nested(location_taxonomy):
    nested = SpatialStrata()
    sub = SpatialStrata()
    sub._direct_files.extend([Path('test1.jpg'), Path('test2.jpg')])
    nested._nested_files['Sub'] = sub
    assert_files(nested.files, 'test1.jpg', 'test2.jpg')


def test_files__deeply_nested(location_taxonomy):
    deep = SpatialStrata()
    deep.add('A::B::C::D::E', Path('deep.jpg'))
    assert_files(deep['A::B::C::D::E'].files, 'deep.jpg')


def test_files__multiple_branches(location_taxonomy):
    neighborhood = location_taxonomy._nested_files['Town']._nested_files['Neighborhood']
    assert_files(neighborhood.files,
        'neighbor.jpg',
        'pond.jpg',
        'park.jpg',

        'neighbor house 01.jpg',
        'neighbor house 02.jpg',
        'neighbor garden.jpg',

        'house 01.jpg',
        'house 02.jpg',
        'house 03.jpg',
        'house 04.jpg',
        'house 05.jpg',
        'house 06.jpg',

        'backyard 01.jpg',
        'backyard 02.jpg',
        'frontyard.jpg',
        'driveway.jpg',
        'pool.jpg',
        'shed.jpg'
    )


def test_files__single_file():
    single = SpatialStrata()
    single._direct_files.append(Path('single.jpg'))
    assert_files(single.files, 'single.jpg')


def test_get__base_case(location_taxonomy):
    assert location_taxonomy[''] == location_taxonomy


def test_get__no_delimiter(location_taxonomy):
    assert location_taxonomy['Vacation'].name == 'Vacation'
    assert location_taxonomy['Town'].name == 'Town'


def test_get__no_delimiter__missing(location_taxonomy):
    with pytest.raises(KeyError):
        _ = location_taxonomy['Missing']


def test_get__single_delimiter(location_taxonomy):
    assert location_taxonomy['Town::Neighborhood'].name == 'Neighborhood'


def test_get__single_delimiter__missing(location_taxonomy):
    with pytest.raises(KeyError):
        _ = location_taxonomy['Town::Bank']


def test_get__multiple_delimiters(location_taxonomy):
    assert location_taxonomy['Town::Neighborhood::Home::Yard'].name == 'Yard'


def test_get__multiple_delimiters__missing(location_taxonomy):
    with pytest.raises(KeyError):
        _ = location_taxonomy['Town::Neighborhood::Park::Courts']


def test_add_files():
    single = SpatialStrata()
    single.add_files(Path('test.jpg'))
    assert_files(single.files, 'test.jpg')


def test_add_files__multiple_file():
    single = SpatialStrata()
    single.add_files(
        Path('test3.jpg'),
        Path('test1.jpg'),
        Path('test2.jpg')
    )
    assert_files(single.files, 'test1.jpg', 'test2.jpg', 'test3.jpg')


def test_add_files__empty():
    single = SpatialStrata()
    single.add_files()
    assert_files(single.files)


def test_nest_stratum__single_level():
    parent = SpatialStrata('Parent')
    child = SpatialStrata('Child')
    parent.nest_stratum(child)
    assert parent['Child'] is child


def test_nest_stratum__multiple_levels():
    root = SpatialStrata('Root')
    level1 = SpatialStrata('Level 1')
    level2 = SpatialStrata('Level 2')
    root.nest_stratum(level1)
    level1.nest_stratum(level2)
    assert root['Level 1']['Level 2'] is level2


def test_nest_stratum__duplicate_name():
    root = SpatialStrata('Root')
    first_child = SpatialStrata('Child')
    duplicate_child = SpatialStrata('Child')

    root.nest_stratum(first_child)
    with pytest.raises(ValueError):
        root.nest_stratum(duplicate_child)


def test_add__base_case(location_taxonomy):
    location_taxonomy.add('', Path('scenic overlook.jpg'))
    assert Path('scenic overlook.jpg') in location_taxonomy._direct_files


def test_add__no_delimiter(location_taxonomy):
    location_taxonomy.add('Vacation', Path('hotel.jpg'))
    assert Path('hotel.jpg') in location_taxonomy._nested_files['Vacation']._direct_files


def test_add__no_delimiter__missing(location_taxonomy):
    location_taxonomy.add('New Place', Path('waterfall.jpg'))
    new = location_taxonomy._nested_files['New Place']
    assert new.name == 'New Place'
    assert Path('waterfall.jpg') in new._direct_files


def test_add__single_delimiter(location_taxonomy):
    location_taxonomy.add('Town::Neighborhood', Path('test.jpg'))
    assert Path('test.jpg') in location_taxonomy._nested_files['Town']._nested_files['Neighborhood']._direct_files


def test_add__single_delimiter__missing(location_taxonomy):
    location_taxonomy.add('Vacation::Hawaii', Path('hawaii.jpg'))
    new = location_taxonomy._nested_files['Vacation']._nested_files['Hawaii']
    assert new.name == 'Hawaii'
    assert Path('hawaii.jpg') in new._direct_files


def test_add__multiple_delimiters(location_taxonomy):
    location_taxonomy.add('Town::Neighborhood::Park', Path('gazebo.jpg'))
    assert Path('gazebo.jpg') in location_taxonomy._nested_files['Town']._nested_files['Neighborhood']._nested_files['Park']._direct_files


def test_add__multiple_delimiters__missing(location_taxonomy):
    location_taxonomy.add('Village::Main Street::Movie Theater', Path('concessions.jpg'))
    village = location_taxonomy._nested_files['Village']
    assert village.name == 'Village'
    main_street = village._nested_files['Main Street']
    assert main_street.name == 'Main Street'
    movie_theater = main_street._nested_files['Movie Theater']
    assert movie_theater.name == 'Movie Theater'
    assert Path('concessions.jpg') in movie_theater._direct_files



