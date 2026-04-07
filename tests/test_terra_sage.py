from pathlib import Path

from metamancer import TerraSage


def test_haversine_distance():
    ny = (40.7128, -74.0060)
    london = (51.5074, -0.1278)
    assert round(TerraSage.haversine_distance(ny, london)) == 5570


def test_haversine_distance__same_point():
    point = (45.0, 45.0)
    assert TerraSage.haversine_distance(point, point) == 0


def test_haversine_distance__equator():
    greenwich = (0.0, 0.0)
    east = (0.0, 90.0)
    assert round(TerraSage.haversine_distance(greenwich, east)) == 10008


def test_haversine_distance__poles():
    north_pole = (90.0, 0.0)
    south_pole = (-90.0, 0.0)
    assert round(TerraSage.haversine_distance(north_pole, south_pole)) == 20015


def test_build_strata():
    taxonomy = TerraSage.build_strata(
        {
            Path('nyc_manhattan_upper.jpg'): (40.7831, -73.9712),
            Path('nyc_manhattan_midtown.jpg'): (40.7589, -73.9851),
            Path('nyc_manhattan_downtown.jpg'): (40.7214, -74.0052),

            Path('nyc_brooklyn_downtown.jpg'): (40.6782, -73.9442),
            Path('nyc_brooklyn_prospect_park.jpg'): (40.6501, -73.9496),

            Path('nyc_queens_flushing.jpg'): (40.7282, -73.7949),
            Path('nyc_queens_jackson_heights.jpg'): (40.7498, -73.8372),

            Path('sf_city_downtown.jpg'): (37.7749, -122.4194),
            Path('sf_city_north_beach.jpg'): (37.8025, -122.4058),
            Path('sf_city_sunset_district.jpg'): (37.7694, -122.4862),

            Path('sf_oakland_downtown.jpg'): (37.8044, -122.2711),
            Path('sf_oakland_east.jpg'): (37.7775, -122.2197),

            Path('chicago_downtown.jpg'): (41.8781, -87.6298),
            Path('chicago_lincoln_park.jpg'): (41.9484, -87.6553),
            Path('chicago_hyde_park.jpg'): (41.7948, -87.5917)
        }, 
        min_distance_threshold=0.005,
        min_subcluster_size=2
    )

    assert len(taxonomy.files) == 15

    total_items = len(taxonomy._direct_files) + len(taxonomy._nested_files)
    assert total_items >= 2, f'Expected at least 2 top-level items, got {total_items}'
    assert len(taxonomy._nested_files) > 0, 'No nested taxonomies were created'

    has_multi_level_nesting = False
    for nested in taxonomy._nested_files.values():
        if len(nested._nested_files) > 0:
            has_multi_level_nesting = True
            break
    assert has_multi_level_nesting, 'No multi-level nesting was created'

    #print('\n--- Taxonomy Structure ---')
    #taxonomy.print()


def test_build_strata__comprehensive():
    taxonomy = TerraSage.build_strata(
        {
            # ===== NORTH AMERICA =====

            # == New York Area ==
            # Manhattan (dense urban cluster)
            Path('nyc_manhattan_upper.jpg'): (40.7831, -73.9712),
            Path('nyc_manhattan_midtown.jpg'): (40.7589, -73.9851),
            Path('nyc_manhattan_downtown.jpg'): (40.7214, -74.0052),
            Path('nyc_manhattan_east_village.jpg'): (40.7425, -73.9878),
            Path('nyc_manhattan_times_square.jpg'): (40.7580, -73.9855),
            Path('nyc_manhattan_empire_state.jpg'): (40.7484, -73.9857),
            Path('nyc_manhattan_grand_central.jpg'): (40.7527, -73.9772),

            # Brooklyn (medium density)
            Path('nyc_brooklyn_downtown.jpg'): (40.6782, -73.9442),
            Path('nyc_brooklyn_prospect_park.jpg'): (40.6501, -73.9496),
            Path('nyc_brooklyn_williamsburg.jpg'): (40.7197, -73.9573),
            Path('nyc_brooklyn_heights.jpg'): (40.6782, -73.9442),
            Path('nyc_brooklyn_park_slope.jpg'): (40.6639, -73.9874),

            # Queens (medium density)
            Path('nyc_queens_flushing.jpg'): (40.7282, -73.7949),
            Path('nyc_queens_jackson_heights.jpg'): (40.7498, -73.8372),
            Path('nyc_queens_long_island_city.jpg'): (40.7429, -73.9188),
            Path('nyc_queens_corona.jpg'): (40.7516, -73.8297),

            # Staten Island (sparse)
            Path('nyc_staten_st_george.jpg'): (40.5795, -74.1502),
            Path('nyc_staten_south_beach.jpg'): (40.5621, -74.1053),

            # New Jersey (nearby but separate cluster)
            Path('nj_hoboken.jpg'): (40.7453, -74.0279),
            Path('nj_jersey_city.jpg'): (40.7282, -74.0776),
            Path('nj_newark.jpg'): (40.7357, -74.1724),

            # == San Francisco Bay Area ==
            # SF City (dense urban cluster)
            Path('sf_city_downtown.jpg'): (37.7749, -122.4194),
            Path('sf_city_north_beach.jpg'): (37.8025, -122.4058),
            Path('sf_city_sunset_district.jpg'): (37.7694, -122.4862),
            Path('sf_city_mission_bay.jpg'): (37.7785, -122.3892),
            Path('sf_city_golden_gate_park.jpg'): (37.7694, -122.4831),
            Path('sf_city_fishermans_wharf.jpg'): (37.8029, -122.4058),

            # Oakland (medium density)
            Path('sf_oakland_downtown.jpg'): (37.8044, -122.2711),
            Path('sf_oakland_east_oakland.jpg'): (37.7775, -122.2197),
            Path('sf_oakland_berkeley.jpg'): (37.8202, -122.2702),
            Path('sf_oakland_alameda.jpg'): (37.7903, -122.2165),

            # South Bay (medium density)
            Path('sf_southbay_san_jose.jpg'): (37.3541, -121.9552),
            Path('sf_southbay_palo_alto.jpg'): (37.4419, -122.1430),
            Path('sf_southbay_santa_clara.jpg'): (37.3688, -122.0363),
            Path('sf_southbay_redwood_city.jpg'): (37.5485, -122.3084),

            # Marin County (sparse)
            Path('sf_marin_san_rafael.jpg'): (37.9735, -122.5311),
            Path('sf_marin_sausalito.jpg'): (37.8985, -122.5250),

            # == Chicago Area ==
            # Downtown (dense)
            Path('chicago_downtown_the_loop.jpg'): (41.8781, -87.6298),
            Path('chicago_downtown_river_north.jpg'): (41.8826, -87.6233),
            Path('chicago_downtown_magnificent_mile.jpg'): (41.8855, -87.6274),
            Path('chicago_downtown_navy_pier.jpg'): (41.8853, -87.6185),
            Path('chicago_downtown_grant_park.jpg'): (41.8675, -87.6166),

            # North Side (medium density)
            Path('chicago_north_lincoln_park.jpg'): (41.9484, -87.6553),
            Path('chicago_north_wicker_park.jpg'): (41.9474, -87.6947),
            Path('chicago_north_lakeview.jpg'): (41.9542, -87.6659),
            Path('chicago_north_wrigleyville.jpg'): (41.9665, -87.6533),

            # South Side (medium density)
            Path('chicago_south_hyde_park.jpg'): (41.7948, -87.5917),
            Path('chicago_south_kenwood.jpg'): (41.7798, -87.6189),
            Path('chicago_south_chinatown.jpg'): (41.8299, -87.6338),

            # Suburbs (sparse)
            Path('chicago_suburbs_evanston.jpg'): (42.0334, -87.6823),
            Path('chicago_suburbs_oak_park.jpg'): (41.8756, -87.8178),

            # == Los Angeles Area ==
            # Downtown LA (dense)
            Path('la_downtown_dtla.jpg'): (34.0522, -118.2437),
            Path('la_downtown_la_live.jpg'): (34.0477, -118.2497),
            Path('la_downtown_arts_district.jpg'): (34.0570, -118.2368),
            Path('la_downtown_echo_park.jpg'): (34.0639, -118.2393),

            # Hollywood (medium density)
            Path('la_hollywood_hollywood_blvd.jpg'): (34.0928, -118.3287),
            Path('la_hollywood_hollywood_hills.jpg'): (34.1016, -118.3267),
            Path('la_hollywood_west_hollywood.jpg'): (34.0837, -118.3590),

            # Santa Monica (medium density)
            Path('la_santamonica_pier.jpg'): (34.0195, -118.4912),
            Path('la_santamonica_third_street_promenade.jpg'): (34.0274, -118.4765),
            Path('la_santamonica_montana_avenue.jpg'): (34.0365, -118.4798),

            # Long Beach (medium density)
            Path('la_longbeach_downtown.jpg'): (33.7701, -118.1937),
            Path('la_longbeach_harbor.jpg'): (33.7605, -118.1855),

            # ===== EUROPE =====

            # == London Area ==
            # Central London (dense)
            Path('london_central_central_london.jpg'): (51.5074, -0.1278),
            Path('london_central_westminster.jpg'): (51.5007, -0.1246),
            Path('london_central_st_pauls.jpg'): (51.5138, -0.0984),
            Path('london_central_tower_bridge.jpg'): (51.5080, -0.0759),
            Path('london_central_trafalgar_square.jpg'): (51.5033, -0.1195),

            # West London (medium density)
            Path('london_west_notting_hill.jpg'): (51.5074, -0.2088),
            Path('london_west_kensington.jpg'): (51.4912, -0.1953),
            Path('london_west_chelsea.jpg'): (51.4817, -0.1905),

            # East London (medium density)
            Path('london_east_shoreditch.jpg'): (51.5203, -0.0293),
            Path('london_east_canary_wharf.jpg'): (51.5085, -0.0235),

            # == Paris Area ==
            # Central Paris (dense)
            Path('paris_central_central_paris.jpg'): (48.8566, 2.3522),
            Path('paris_central_eiffel_tower.jpg'): (48.8584, 2.2945),
            Path('paris_central_louvre.jpg'): (48.8606, 2.3376),
            Path('paris_central_notre_dame.jpg'): (48.8530, 2.3499),
            Path('paris_central_arc_de_triomphe.jpg'): (48.8738, 2.2950),

            # Outer Paris (medium density)
            Path('paris_outer_montmartre.jpg'): (48.8971, 2.3838),
            Path('paris_outer_montparnasse.jpg'): (48.8302, 2.3547),
            Path('paris_outer_latin_quarter.jpg'): (48.8464, 2.3591),

            # ===== ASIA =====

            # == Tokyo Area ==
            # Central Tokyo (dense)
            Path('tokyo_central_shinjuku.jpg'): (35.6762, 139.6503),
            Path('tokyo_central_shibuya.jpg'): (35.6895, 139.6917),
            Path('tokyo_central_tokyo_tower.jpg'): (35.6586, 139.7454),
            Path('tokyo_central_tokyo_station.jpg'): (35.6828, 139.7530),
            Path('tokyo_central_asakusa.jpg'): (35.7100, 139.8107),

            # Yokohama (medium density)
            Path('tokyo_yokohama_station.jpg'): (35.4437, 139.6380),
            Path('tokyo_yokohama_minato_mirai.jpg'): (35.4511, 139.6309),

            # ===== AUSTRALIA =====

            # == Sydney Area ==
            # Central Sydney (dense)
            Path('sydney_central_sydney_cbd.jpg'): (-33.8688, 151.2093),
            Path('sydney_central_opera_house.jpg'): (-33.8568, 151.2153),
            Path('sydney_central_the_rocks.jpg'): (-33.8523, 151.2108),
            Path('sydney_central_darling_harbour.jpg'): (-33.8912, 151.1990),

            # Bondi (medium density)
            Path('sydney_bondi_beach.jpg'): (-33.8915, 151.2767),
            Path('sydney_bondi_junction.jpg'): (-33.8854, 151.2698),

            # ===== ISOLATED POINTS =====
            # These points are far from any cluster to test handling of outliers
            Path('isolated_hawaii.jpg'): (21.3069, -157.8583),
            Path('isolated_alaska.jpg'): (61.2181, -149.9003),
            Path('isolated_moscow.jpg'): (55.7558, 37.6173),
            Path('isolated_capetown.jpg'): (-33.9249, 18.4241),
            Path('isolated_rio.jpg'): (-22.9068, -43.1729)
        },
        min_distance_threshold=0.005,
        min_subcluster_size=2
    )

    assert len(taxonomy.files) == 99

    # Define expected structure
    # We expect:
    # 1. Multiple top-level clusters (continents/regions)
    # 2. Each continent should have subclusters (cities)
    # 3. Each city should have subclusters (neighborhoods)
    # 4. Isolated points should be in their own clusters or directly in the root

    #print("\n--- Comprehensive Test Taxonomy Structure ---")
    #taxonomy.print()

    # Verify basic structure expectations
    # We should have at least 4 top-level items (representing major geographic regions)
    total_top_level = len(taxonomy._direct_files) + len(taxonomy._nested_files)
    assert total_top_level >= 4, f'Expected at least 4 top-level items, got {total_top_level}'

    # We should have nested taxonomies (representing cities within regions)
    assert len(taxonomy._nested_files) > 0, 'No nested taxonomies were created'

    # We should have multi-level nesting (neighborhoods within cities)
    multi_level_count = 0
    for region in taxonomy._nested_files.values():
        for city in region._nested_files.values():
            if len(city._nested_files) > 0:
                multi_level_count += 1
                break
    assert multi_level_count >= 2, f'Expected at least 2 instances of multi-level nesting, got {multi_level_count}'

    # Verify specific file groupings
    # Helper function to find files in the taxonomy
    def find_files_in_taxonomy(taxonomy, file_pattern):
        """Find all files in the taxonomy that match the given pattern."""
        matching_files = []

        # Check direct files
        for file in taxonomy._direct_files:
            if file_pattern in file.name:
                matching_files.append(file)

        # Check nested taxonomies
        for nested in taxonomy._nested_files.values():
            matching_files.extend(find_files_in_taxonomy(nested, file_pattern))

        return matching_files

    # Helper function to find the smallest taxonomy containing all the specified files
    def find_containing_taxonomy(taxonomy, file_patterns):
        """Find the smallest taxonomy that contains all files matching the patterns."""
        # Check if this taxonomy contains all the files
        all_contained = True
        for pattern in file_patterns:
            if not find_files_in_taxonomy(taxonomy, pattern):
                all_contained = False
                break

        if all_contained:
            # Check if any child taxonomy contains all the files
            for nested in taxonomy._nested_files.values():
                child_result = find_containing_taxonomy(nested, file_patterns)
                if child_result:
                    return child_result

            # If no child contains all files, but this one does, return this one
            return taxonomy

        # This taxonomy doesn't contain all the files
        return None

    # Verify that New York files are grouped together
    nyc_taxonomy = find_containing_taxonomy(taxonomy, ['nyc_'])
    assert nyc_taxonomy is not None, 'New York files should be grouped together'

    # Verify that Manhattan files are grouped together
    manhattan_taxonomy = find_containing_taxonomy(taxonomy, ['nyc_manhattan_'])
    assert manhattan_taxonomy is not None, 'Manhattan files should be grouped together'

    # Verify that San Francisco and Chicago are in separate clusters
    sf_taxonomy = find_containing_taxonomy(taxonomy, ['sf_city_'])
    chicago_taxonomy = find_containing_taxonomy(taxonomy, ['chicago_downtown_'])

    # They should both exist
    assert sf_taxonomy is not None, 'San Francisco files should be grouped together'
    assert chicago_taxonomy is not None, 'Chicago files should be grouped together'

    # And they should be different taxonomies
    assert sf_taxonomy != chicago_taxonomy, 'San Francisco and Chicago should be in separate clusters'

    # Verify that isolated points are not grouped with major clusters
    # For each isolated point, find its containing taxonomy
    for isolated in ['isolated_hawaii', 'isolated_alaska', 'isolated_moscow', 
                     'isolated_capetown', 'isolated_rio']:
        isolated_taxonomy = find_containing_taxonomy(taxonomy, [isolated])
        assert isolated_taxonomy is not None, f'{isolated} should be in the taxonomy'

        # The isolated point should not be in the same taxonomy as any major city
        assert isolated_taxonomy != nyc_taxonomy, f'{isolated} should not be grouped with New York'
        assert isolated_taxonomy != sf_taxonomy, f'{isolated} should not be grouped with San Francisco'
        assert isolated_taxonomy != chicago_taxonomy, f'{isolated} should not be grouped with Chicago'
