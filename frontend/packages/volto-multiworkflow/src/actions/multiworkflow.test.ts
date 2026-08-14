import { describe, expect, it } from 'vitest';
import {
  GET_MULTIWORKFLOW,
  TRANSITION_MULTIWORKFLOW,
  getMultiWorkflow,
  transitionMultiWorkflow,
} from './multiworkflow';

describe('getMultiWorkflow', () => {
  it('requests the workflow endpoint', () => {
    const action = getMultiWorkflow('/a-document');

    expect(action.type).toBe(GET_MULTIWORKFLOW);
    expect(action.request).toEqual({
      op: 'get',
      path: '/a-document/@workflow',
    });
  });

  it('flattens a backend URL', () => {
    const action = getMultiWorkflow('http://localhost:8080/Plone/a-document');

    expect(action.request.path).toBe('/a-document/@workflow');
  });
});

describe('transitionMultiWorkflow', () => {
  it('posts to the transition', () => {
    const action = transitionMultiWorkflow('/a-document/@workflow/activate');

    expect(action.type).toBe(TRANSITION_MULTIWORKFLOW);
    expect(action.request).toEqual({
      op: 'post',
      path: '/a-document/@workflow/activate',
      data: {},
    });
  });

  it('flattens the absolute @id the payload carries', () => {
    // Transition ids arrive as absolute backend URLs; posting one unflattened
    // sends the request to the wrong path.
    const action = transitionMultiWorkflow(
      'http://localhost:8080/Plone/a-document/@workflow/activate',
    );

    expect(action.request.path).toBe('/a-document/@workflow/activate');
  });
});
