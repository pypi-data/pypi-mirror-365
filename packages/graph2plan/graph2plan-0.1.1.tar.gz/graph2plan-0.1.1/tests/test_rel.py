import pytest

from graph2plan.dcel.external import fully_embed_graph
from graph2plan.dual.create_rectangular_floorplan import merge_domains
from graph2plan.dual.create_rectangular_floorplan import (
    create_dual_and_calculate_domains,
)
from graph2plan.fourtp.faces import get_embedding_of_four_complete_G
from graph2plan.rel.rel2 import create_rel, extract_graphs
from graph2plan.dual.helpers import check_is_source_target_graph


@pytest.fixture()
def create_rel_kk85(saved_co_kk85):
    G_c, co_vertices, pos = saved_co_kk85
    embedding = get_embedding_of_four_complete_G(G_c, pos)
    Grel = create_rel(G_c, co_vertices, embedding)
    T1, T2 = extract_graphs(Grel)
    return T1, T2, pos


def test_kk85_rel_yields_st_graphs(create_rel_kk85):
    T1, T2, _ = create_rel_kk85
    check_is_source_target_graph(T1)
    check_is_source_target_graph(T2)


def test_kk85_st_graphs_yield_dual(create_rel_kk85):
    T1, T2, pos = create_rel_kk85
    res1 = fully_embed_graph(T1, pos, "y")
    res2 = fully_embed_graph(T2, pos, "x")
    x_domains = create_dual_and_calculate_domains(res1, "y", True)
    y_domains = create_dual_and_calculate_domains(res2, "x", True)
    merged_doms = merge_domains(x_domains, y_domains)
    # TODO some tests on the merged domains -> like adjacent to south in four-completed graph is adjacent in the merged doms..
    assert merged_doms
