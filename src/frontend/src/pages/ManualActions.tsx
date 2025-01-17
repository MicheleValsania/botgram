import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import api, { InstagramAction } from '../services/api';
import { useFormik } from 'formik';
import * as Yup from 'yup';

const ManualActions: React.FC = () => {
  const { session } = useSession();
  const [status, setStatus] = useState<{ success?: string; error?: string }>({});

  const formik = useFormik({
    initialValues: {
      action_type: 'follow',
      target_user_id: '',
      media_id: '',
      comment_text: '',
    },
    validationSchema: Yup.object({
      action_type: Yup.string()
        .required('Required')
        .oneOf(['follow', 'like', 'comment']),
      target_user_id: Yup.string()
        .when('action_type', {
          is: 'follow',
          then: schema => schema.required('Required for follow action'),
        }),
      media_id: Yup.string()
        .when('action_type', {
          is: (val: string) => ['like', 'comment'].includes(val),
          then: schema => schema.required('Required for like/comment action'),
        }),
      comment_text: Yup.string()
        .when('action_type', {
          is: 'comment',
          then: schema => schema.required('Required for comment action')
            .min(2, 'Comment must be at least 2 characters')
            .max(2200, 'Comment must be at most 2200 characters'),
        }),
    }),
    onSubmit: async (values, { setSubmitting, resetForm }) => {
      if (!session) return;

      setStatus({});
      try {
        const action: InstagramAction = {
          username: session.username,
          action_type: values.action_type as 'follow' | 'like' | 'comment',
          target_user_id: values.target_user_id,
          media_id: values.media_id,
          comment_text: values.comment_text,
        };

        let response;
        switch (values.action_type) {
          case 'follow':
            response = await api.followUser(action);
            break;
          case 'like':
            response = await api.likePost(action);
            break;
          case 'comment':
            response = await api.commentPost(action);
            break;
        }

        if (response?.data.success) {
          setStatus({ success: `${values.action_type} action completed successfully` });
          resetForm();
        }
      } catch (err) {
        setStatus({ error: err instanceof Error ? err.message : 'Action failed' });
      } finally {
        setSubmitting(false);
      }
    },
  });

  if (!session) return null;

  return (
    <div className="container">
      <h1 className="mb-4">Manual Actions</h1>

      {status.success && (
        <div className="alert alert-success" role="alert">
          {status.success}
        </div>
      )}

      {status.error && (
        <div className="alert alert-danger" role="alert">
          {status.error}
        </div>
      )}

      <div className="card">
        <div className="card-body">
          <form onSubmit={formik.handleSubmit}>
            <div className="mb-3">
              <label htmlFor="action_type" className="form-label">
                Action Type
              </label>
              <select
                id="action_type"
                className={`form-select ${
                  formik.touched.action_type && formik.errors.action_type
                    ? 'is-invalid'
                    : ''
                }`}
                {...formik.getFieldProps('action_type')}
              >
                <option value="follow">Follow User</option>
                <option value="like">Like Post</option>
                <option value="comment">Comment on Post</option>
              </select>
              {formik.touched.action_type && formik.errors.action_type && (
                <div className="invalid-feedback">
                  {formik.errors.action_type}
                </div>
              )}
            </div>

            {formik.values.action_type === 'follow' && (
              <div className="mb-3">
                <label htmlFor="target_user_id" className="form-label">
                  Target User ID
                </label>
                <input
                  type="text"
                  id="target_user_id"
                  className={`form-control ${
                    formik.touched.target_user_id && formik.errors.target_user_id
                      ? 'is-invalid'
                      : ''
                  }`}
                  {...formik.getFieldProps('target_user_id')}
                />
                {formik.touched.target_user_id && formik.errors.target_user_id && (
                  <div className="invalid-feedback">
                    {formik.errors.target_user_id}
                  </div>
                )}
              </div>
            )}

            {(formik.values.action_type === 'like' ||
              formik.values.action_type === 'comment') && (
              <div className="mb-3">
                <label htmlFor="media_id" className="form-label">
                  Media ID
                </label>
                <input
                  type="text"
                  id="media_id"
                  className={`form-control ${
                    formik.touched.media_id && formik.errors.media_id
                      ? 'is-invalid'
                      : ''
                  }`}
                  {...formik.getFieldProps('media_id')}
                />
                {formik.touched.media_id && formik.errors.media_id && (
                  <div className="invalid-feedback">{formik.errors.media_id}</div>
                )}
              </div>
            )}

            {formik.values.action_type === 'comment' && (
              <div className="mb-3">
                <label htmlFor="comment_text" className="form-label">
                  Comment Text
                </label>
                <textarea
                  id="comment_text"
                  className={`form-control ${
                    formik.touched.comment_text && formik.errors.comment_text
                      ? 'is-invalid'
                      : ''
                  }`}
                  {...formik.getFieldProps('comment_text')}
                />
                {formik.touched.comment_text && formik.errors.comment_text && (
                  <div className="invalid-feedback">
                    {formik.errors.comment_text}
                  </div>
                )}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary"
              disabled={formik.isSubmitting}
            >
              {formik.isSubmitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" />
                  Executing...
                </>
              ) : (
                'Execute Action'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ManualActions;
